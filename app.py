from flask import Flask, render_template, abort

app = Flask(__name__)

# Fake product catalog (clearly ridiculous scam items)
PRODUCTS = [
    {
        "id": "1",
        "name": "Sunlight in a Jar",
        "price": "$199.99",
        "short": "Guaranteed 100% sunlight — bottled fresh!",
        "desc": "Contains: air, optimism, and a hint of citrus. Not responsible for cloud cover.",
        "scam_note": "This is a parody product used to teach how ridiculous some listings can be. It's not real."
    },
    {
        "id": "2",
        "name": "Invisible Ink Anti-Theft Spray",
        "price": "$299.99",
        "short": "Spray your valuables and they become 'invisible' to thieves.",
        "desc": "Also works as a mild room freshener if you like the scent of mystery.",
        "scam_note": "Parody item; invisibility not scientifically verified."
    },
    {
        "id": "3",
        "name": "Guaranteed Riches Ebook — Click Now!",
        "price": "$999.99",
        "short": "Secrets to instant wealth (results may vary).",
        "desc": "Includes 10 steps, 3 magical rituals, and one coupon code.",
        "scam_note": "Educational parody: real financial advice requires work, not a single ebook."
    }
]


@app.route('/')
def index():
    return render_template('index.html', products=PRODUCTS)


@app.route('/product/<product_id>')
def product(product_id):
    prod = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not prod:
        abort(404)
    return render_template('product.html', product=prod)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
