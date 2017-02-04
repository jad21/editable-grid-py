from src import EditableGrid
from flask import Flask, Response, render_template, request
app = Flask(__name__, static_folder="pub")


@app.route("/src/xml")
def render_xml():
    return Response(get_data("xml"), mimetype='text/xml')


@app.route("/src/json")
def render_json():
    return get_data("json")


@app.route("/")
def views():
    if "xml" in request.args:
        return render_template("index_xml.html")
    else:
        return render_template("index_json.html")


def get_data(format_="xml"):
    grid = EditableGrid("utf-8", True)
    grid.addColumn("name", "NAME", "string")
    grid.addColumn("firstname", "FIRSTNAME", "string")

    grid.addColumn("age", "AGE", "integer")
    grid.addColumn("height", "HEIGHT", "double(m,2)", None, True, None, False)

    # add column with predefined values, organized in "option groups" (dropdown list)
    grid.addColumn("country", "COUNTRY", "string", {
        "Europe": {"be": "Belgium", "fr": "France", "uk": "Great-Britain", "nl": "Nederland"},
        "America": {"br": "Brazil", "ca": "Canada", "us": "USA"},
        "Africa": {"ng": "Nigeria", "za": "South-Africa", "zw": "Zimbabwe"}
    })

    # add some other columns: email, url, boolean, date
    grid.addColumn("email", "EMAIL", "email")
    # grid.addColumn("website", "WEBSITE", "url")
    grid.addColumn("freelance", "FREELANCE", "boolean")
    grid.addColumn("lastvisit", "LAST VISIT", "date")

    # action column ("html" type), not editable
    grid.addColumn("action", "", "html", None, False)

    data = []
    with open("demo.csv", "r", encoding='utf-8') as f:
        for line in f.readlines():
            row = line.split(";")
            if len(row) <= 1 or row[0] == 'id':
                continue
            # if len(data) > 3:
                # break
            data.append({
                "id": row[0],
                "name": row[1],
                "firstname": row[2],
                "age": row[3],
                "height": row[4],
                "continent": row[5],
                "country": row[6],
                "email": row[7],
                "freelance": row[8] == '1',
                "lastvisit": row[9],
                "website": row[10]
            })
    if format_ == 'xml':
        xml = grid.getXML(data)
        return xml
    else:
        return grid.getJSON(data)


if __name__ == "__main__":
    app.run()