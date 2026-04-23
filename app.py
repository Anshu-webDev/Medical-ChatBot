import json
from flask import Flask, render_template, request, jsonify
from chatbot import get_response, KB_PATH, knowledge_base

app = Flask(__name__)


def save_knowledge_base():
    with open(KB_PATH, "w") as f:
        json.dump(knowledge_base, f, indent=2)


@app.route("/")
def index():
    return render_template("index.html", company=knowledge_base["company"])


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Please type a message."})
    return jsonify({"response": get_response(user_message)})


@app.route("/admin")
def admin():
    return render_template("admin.html", company=knowledge_base["company"], faqs=knowledge_base["faqs"])


@app.route("/admin/add", methods=["POST"])
def add_qna():
    data = request.json
    keywords = [k.strip().lower() for k in data.get("keywords", "").split(",") if k.strip()]
    response = data.get("response", "").strip()

    if not keywords or not response:
        return jsonify({"success": False, "message": "Keywords and response are required."}), 400

    knowledge_base["faqs"].append({"keywords": keywords, "response": response})
    save_knowledge_base()
    return jsonify({"success": True, "message": "Q&A added successfully!"})


@app.route("/admin/delete/<int:index>", methods=["DELETE"])
def delete_qna(index):
    if index < 0 or index >= len(knowledge_base["faqs"]):
        return jsonify({"success": False, "message": "Invalid index."}), 400
    knowledge_base["faqs"].pop(index)
    save_knowledge_base()
    return jsonify({"success": True, "message": "Q&A deleted successfully!"})


if __name__ == "__main__":
    app.run(debug=True)
