import matplotlib
matplotlib.use("Agg")  
from flask import Flask, render_template, request, send_file, session
import matplotlib.pyplot as plt
import io
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)

app.config["SESSION_TYPE"] = "filesystem"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        principal = float(request.form["principal"])
        rate = float(request.form["rate"])
        years = int(request.form["years"])
        times_per_year = int(request.form["times_per_year"])
        annual_contribution = float(request.form.get("annual_contribution", 0))  # Default to 0 if not provided
    except KeyError as e:
        return f"Missing form input: {e}", 400

    amounts = []
    for year in range(1, years + 1):
        amount = principal * (1 + (rate / (100 * times_per_year))) ** (times_per_year * year)
        for i in range(year):
            amount += annual_contribution * ((1 + (rate / 100)) ** (year - i))
        amounts.append(amount)

    session["graph_data"] = {"years": list(range(1, years + 1)), "amounts": amounts}

    total_amount = amounts[-1]
    interest = total_amount - (principal + annual_contribution * years)

    return render_template(
        "index.html",
        principal=principal,
        rate=rate,
        years=years,
        times_per_year=times_per_year,
        annual_contribution=annual_contribution,
        amount=round(total_amount, 2),
        interest=round(interest, 2),
        graph_available=True
    )


@app.route("/graph")
def graph():
    graph_data = session.get("graph_data", None)
    if not graph_data:
        return "Graph data unavailable.", 404

    plt.figure(figsize=(10, 6))
    plt.plot(graph_data["years"], graph_data["amounts"], marker="o", label="Investment Growth")
    plt.title("Compound Interest Growth Over Time")
    plt.xlabel("Years")
    plt.ylabel("Total Amount (€)")
    plt.grid(True)
    plt.legend()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()

    return send_file(img, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
