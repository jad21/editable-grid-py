from src import EditableGrid
from flask import Flask, Response, render_template, request
app = Flask(__name__, static_folder="pub")


@app.route("/src/xml")
def render_xml():
    return Response(Data().all("xml"), mimetype='text/xml')


@app.route("/src/json")
def render_json():
    return Data().all("json")


@app.route("/data/insert", methods=["POST"])
def data_insert():
    json = dict((key, request.form.get(key)) for key in request.form.keys())
    Data().create(**json)
    return "success"

@app.route("/data/update", methods=["POST"])
def data_update():
    json = dict((key, request.form.get(key)) for key in request.form.keys())
    Data().update(**json)
    # Data().update(**{"id":6, "name": "maria"})
    return "success"


@app.route("/data/remove", methods=['GET', "DELETE"])
def data_remove():
    print(request.args)
    Data().delete(request.args.get("id"))
    return "success"


@app.route("/")
def views():
    if "xml" in request.args:
        return render_template("index_xml.html")
    else:
        return render_template("index_json.html")


class Data(object):
    def all(self, format_="xml"):
        grid = EditableGrid("utf-8", True)
        grid.addColumn("name", "NAME", "string")
        grid.addColumn("firstname", "FIRSTNAME", "string")

        grid.addColumn("age", "AGE", "integer")
        grid.addColumn("height", "HEIGHT", "double(m,2)", None, True, None, False)

        grid.addColumn("continent", "CONTINENT", "string", None, True, None, True, True)
        # add column with predefined values, organized in "option groups" (dropdown list)
        grid.addColumn("country", "COUNTRY", "string", {
            "Europe": {"be": "Belgium", "fr": "France", "uk": "Great-Britain", "nl": "Nederland"},
            "America": {"br": "Brazil", "ca": "Canada", "us": "USA"},
            "Africa": {"ng": "Nigeria", "za": "South-Africa", "zw": "Zimbabwe"}
        })

        # add some other columns: email, url, boolean, date
        grid.addColumn("email", "EMAIL", "email")
        grid.addColumn("website", "WEBSITE", "url")
        grid.addColumn("freelance", "FREELANCE", "boolean")
        grid.addColumn("lastvisit", "LAST VISIT", "date")

        # action column ("html" type), not editable
        grid.addColumn("action", "", "html", None, False)

        data = []
        with open("demo.csv", "r") as f:
            for line in f.readlines():
                row = line.split(";")
                if len(row) <= 1 or row[0] == 'id':
                    continue

                # if len(data) > 3:
                #     break

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
            return grid.renderXML(data)
        else:
            print("here json")
            return grid.getJSON(data)

    def create(self, **json):
        row_new = "{id};{name};{firstname};{age};{height};{continent};{country};{email};{freelance};{lastvisit};{website}".format(**json)
        f = open("demo.csv", 'a')
        print(row_new)
        f.write(row_new)
        f.close()

    def delete(self, id):
        f = open("demo.csv", "r+")
        d = f.readlines()
        f.seek(0)
        for line in d:
            row = line.split(";")
            if row[0] != id:
                f.write(line)
        f.truncate()
        f.close()

    def update(self, **json):
        search_id = json["id"]
        del json["id"]
        f = open("demo.csv", "r+")
        d = f.readlines()
        f.seek(0)
        print("search ", search_id)
        for line in d:
            id, name, firstname, age, height, continent, country, email, freelance, lastvisit, website = line.split(";")
            if id == 'id':
                continue
            elif id == search_id:

                old = {"id": id, "name": name, "firstname": firstname, "age": age, "height": height, "continent": continent, "country": country, "email": email, "freelance": freelance, "lastvisit": lastvisit, "website": website}
                for k, v in json.items():
                    old[k] = v.replace(";", "")
                row_new = "{id};{name};{firstname};{age};{height};{continent};{country};{email};{freelance};{lastvisit};{website}".format(**old)
                print(row_new)
                f.write(row_new)
            else:
                f.write(line)

        f.truncate()
        f.close()
        print("updated ", search_id)


if __name__ == "__main__":
    app.run()
    # Data().update(**{"id":6, "name": "maria"})
    # s = "6;Hoffman (copy);Tatyäna;88;1.32;af;ca;Nam@quisdiamluctus.org;1;17/04/2012;www.qktogkjbsvz.rdh"
