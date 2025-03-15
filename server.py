from flask import Flask, render_template, request, jsonify
import json
import random

app = Flask(__name__)

# Load data from JSON file
with open('data.json', 'r') as f:
    restaurants = json.load(f)

# Save data to JSON file
def save_data():
    with open("data.json", "w") as f:
        json.dump(restaurants, f, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get("q", "")
    results = []
    if query:
        query_lower = query.lower()
        for restaurant in restaurants:
            in_title = query_lower in restaurant.get("title", "").lower()
            in_style = any(query_lower in s.lower() for s in restaurant.get("style", []))
            in_dishes = any(query_lower in dish.lower() for dish in restaurant.get("popular_dishes", []))
            if in_title or in_style or in_dishes:
                results.append(restaurant)
    return render_template("search.html", query=query, results=results)

@app.route('/view/<int:res_id>')
def view_details(res_id):
    # Find the matching item by id
    chosen = next((r for r in restaurants if r['id'] == res_id), None)
    if not chosen:
        return "Item not found", 404
    return render_template('view.html', item=chosen, data=restaurants)

@app.route('/api/popular')
def get_popular():
    # Return 4 random restaurants or all if < 4
    if len(restaurants) <= 4:
        return jsonify(restaurants)
    sample = random.sample(restaurants, 4)
    return jsonify(sample)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'GET':
        # Render the add new item form
        return render_template("add.html")
    elif request.method == 'POST':
        data = request.get_json()
        # Validate required fields
        required_fields = ["title", "image", "description", "price_range", "rating", "location", "style", "popular_dishes"]
        for field in required_fields:
            if field not in data or not data[field]:
                return f"Field '{field}' is required.", 400
        try:
            rating = float(data["rating"])
        except ValueError:
            return "Rating must be a number.", 400
        
        # Generate a new id
        new_id = max([r["id"] for r in restaurants], default=0) + 1
        new_item = {
            "id": new_id,
            "title": data["title"],
            "image": data["image"],
            "description": data["description"],
            "price_range": data["price_range"],
            "rating": rating,
            "location": data["location"],
            "style": data["style"],
            "popular_dishes": data["popular_dishes"]
        }
        restaurants.append(new_item)
        save_data()
        return jsonify({"id": new_id})
    
@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    # Find the item by id
    item = next((r for r in restaurants if r["id"] == item_id), None)
    if not item:
        return "Item not found", 404

    if request.method == 'GET':
        return render_template("edit.html", item=item)
    elif request.method == 'POST':
        data = request.get_json()
        # Validate required fields
        required_fields = ["title", "image", "description", "price_range", "rating", "location", "style", "popular_dishes"]
        for field in required_fields:
            if field not in data or not data[field]:
                return f"Field '{field}' is required.", 400
        try:
            rating = float(data["rating"])
        except ValueError:
            return "Rating must be a number.", 400
        
        # Update the item with new data
        item["title"] = data["title"]
        item["image"] = data["image"]
        item["description"] = data["description"]
        item["price_range"] = data["price_range"]
        item["rating"] = rating
        item["location"] = data["location"]
        item["style"] = data["style"]
        item["popular_dishes"] = data["popular_dishes"]
        save_data()
        return jsonify({"id": item_id})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
