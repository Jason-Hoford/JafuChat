from flask import Flask, request, jsonify, render_template, send_file
from jafuGPT import get_answer_from_gpt, setup_llm, get_file_from_db, get_know_base, get_llm
from configuration import get_base_dir, get_port
import webbrowser

from utilsOllama import get_models

app = Flask(__name__)


@app.route('/')
def index():
    if 'settings' in  request.args:
        print("index", request.args['settings'])
        return settings(request.args['settings'])
    links = get_links()
    llm = get_llm()
    return render_template('./index.html', base=get_base_dir(), links=links, model=llm)


def settings(foo):
    links = get_links()
    llm = get_llm()
    models = get_models()
    return render_template('./pick_model.html', base=get_base_dir(), models=models, model=llm)


@app.route("/<string:path>")
def doc_str(path):
    print("doc_str", path)
    links = get_links()
    llm = get_llm()
    return render_template('./index.html', base=path, links=links, model=llm)


@app.route("/#<string:path>")
def select_models(path):
    print("select_models", path)
    links = get_links()
    llm = get_llm()
    return render_template('./index.html', base="demo", links=links, model=llm)


@app.route("/<path:path>")
def doc_path(path):
    print("doc_path", path)
    file = get_file_from_db(path)
    return send_file(file, "application/pdf")


@app.route('/api/query', methods=['POST'])
def process_query():
    print("query")
    query = request.json.get('query')
    base = request.json.get('base')
    print("base:", base)
    if query is None:
        return jsonify({'error': 'Query not provided'}), 400

    # Process the query using your Python script
    answer, docs = get_answer_from_gpt(query, base)
    out = answer
    if len(docs) > 0:
        out += "<ul>\n"
        for d in docs:
            src = d.metadata["source"]
            number = -1
            if 'page' in d.metadata.keys():
                number = d.metadata["page"]
            out = out + "<li>" + ref_to_string(base, src, number) + "</li>"
        out += "</ul>"
    return jsonify({'answer': out})


def get_links():
    list = get_know_base()
    links = []
    for dir in list:
        links.append({"href": "./" + dir, "text": dir})
    return links


def ref_to_string(base, file, page_number):
    html_file = file.replace(" ", "%20")
    name = base + "/" + html_file[html_file.rindex('\\') + 1:]
    # return f'<a href="file:///{html_file}#page={page_number}">{file}({page_number})</a>'
    if page_number == -1:
        return f'<a href="{name}">{file}</a>'
    return f'<a href="{name}#page={page_number}">{file}({page_number})</a>'


if __name__ == '__main__':
    # setup_llm("demo")
    webbrowser.open_new("http://127.0.0.1:" + str(get_port()))
    print("launch browser")
    # app.run(debug=True)
    print("run app infrastructure")
    from waitress import serve

    serve(app, host="0.0.0.0", port=get_port())
