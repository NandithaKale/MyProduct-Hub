from flask import Flask, render_template, request, redirect, url_for, flash
from db_config import get_db_connection
from decimal import Decimal

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def product_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.product_id, p.name AS product_name, p.price, p.quantity, c.category_name
        FROM products p LEFT JOIN categories c ON p.category_id = c.category_id
        ORDER BY p.product_id
    """)
    products = cursor.fetchall()
    cursor.execute("SELECT * FROM categories ORDER BY category_name")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('product_list.html', products=products, categories=categories)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']
        category_id = request.form.get('category_id')
        try:
            cursor.execute(
                "INSERT INTO products (name, price, quantity, category_id) VALUES (%s, %s, %s, %s)",
                (name, price, quantity, category_id)
            )
            conn.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('product_list'))
        except Exception as e:
            flash(f'Error adding product: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.execute("SELECT * FROM categories ORDER BY category_name")
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('add_product.html', categories=categories)

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']
        category_id = request.form.get('category_id')
        try:
            cursor.execute("""
                UPDATE products SET name=%s, price=%s, quantity=%s, category_id=%s WHERE product_id=%s
            """, (name, price, quantity, category_id, product_id))
            conn.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('product_list'))
        except Exception as e:
            flash(f'Error updating product: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        cursor.execute("SELECT * FROM categories ORDER BY category_name")
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        if product:
            return render_template('update_product.html', product=product, categories=categories)
        else:
            flash('Product not found', 'warning')
            return redirect(url_for('product_list'))

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting product: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('product_list'))

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category_name = request.form['category_name']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO categories (category_name) VALUES (%s)", (category_name,))
            conn.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('product_list'))
        except Exception as e:
            flash(f'Error adding category: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('add_category.html')

@app.route('/apply_discount', methods=['GET', 'POST'])
def apply_discount():
    if request.method == 'POST':
        try:
            discount = float(request.form['discount'])
            if not (0 <= discount <= 100):
                flash("Discount must be between 0 and 100", "warning")
                return redirect(url_for('apply_discount'))
        except ValueError:
            flash("Invalid discount value", "danger")
            return redirect(url_for('apply_discount'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT product_id, price FROM products")
        products = cursor.fetchall()

        try:
            for product in products:
                original_price = product['price']
                # Convert Decimal to float for calculation
                original_price_float = float(original_price)
                new_price = original_price_float * (1 - discount / 100)
                cursor.execute("UPDATE products SET price = %s WHERE product_id = %s", (round(new_price, 2), product['product_id']))
            conn.commit()
            flash(f"Discount of {discount}% applied to all products.", "success")
        except Exception as e:
            flash(f"Error applying discount: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('product_list'))
    return render_template('apply_discount.html')

if __name__ == '__main__':
    app.run(debug=True)
