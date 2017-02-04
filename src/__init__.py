# -*- coding: utf-8 -*-
import lxml.etree as ET
import base64
import json


class EditableGrid(object):
    """docstring for EditableGrid"""

    columns = None
    encoding = None
    # write column names in XML and JSON (set to False to save bandwidth)
    writeColumnNames = None
    formatXML = None
    paginator = None

    def __init__(self, encoding="utf-8", writeColumnNames=False, formatXML=False):
        self.encoding = encoding
        self.columns = {}
        self.writeColumnNames = writeColumnNames
        self.formatXML = formatXML
        self.paginator = None

    def getColumnLabels(self):
        labels = {}
        for name, column in self.columns.items():
            labels[name] = column['label']
        return labels

    def getColumnFields(self):
        fields = {}
        for name, column in self.columns.items():
            fields[name] = column['field']
        return fields

    def getColumnTypes(self):
        types = {}
        for name, column in self.columns.items():
            types[name] = column['type']
        return types

    def getColumnValues(self):
        values = {}
        for name, column in self.columns.items():
            values[name] = column['values']
        return values

    def addColumn(self, name, label, _type, values=None, editable=True, field=None, bar=True, hidden=False):
        self.columns[name] = {"field": field if field else name, "label": label, "type": _type, "editable": editable, "bar": bar, "hidden": hidden, "values": values}
        return self

    def setHiddenColumns(self, columns):
        for x in columns:
            if type(columns[x]) is dict:
                columns[x]['hidden'] = True
        return self

    def setPaginator(self, pageCount, totalRowCount, unfilteredRowCount, customAttributes=None):
        """
            Set parameters needed for server-side pagination
            @param integer pageCount number of pages
            @param integer totalRowCount total numer of rows in all pages
            @param integer unfilteredRowCount total number of rows, not taking the filter into account
        """
        self.paginator = {"pagecount": pageCount, "totalrowcount": totalRowCount, "customAttributes": unfilteredRowCount}
        if type(customAttributes) is dict:
            for k, v in customAttributes:
                self.paginator[k] = v

    def _getRowField(self, row, field):
        value = ""
        if type(row) is dict and field in row:
            value = row[field]
        return value

    def getXML(self, rows=False, customRowAttributes=False, encodeCustomAttributes=False, includeMetadata=True):
        table = ET.Element("table")

        if includeMetadata:
            metadata = ET.SubElement(table, "metadata")
            for name, info in self.columns.items():
                attr = {
                    "name": name,
                    "label": info["label"],
                    "datatype": info["type"],
                    "editable": "true" if info['editable'] else "false"
                }
                if 'bar' not in info:
                    attr["bar"] = "false"
                if 'hidden' in info:
                    attr["hidden"] = "true"

                column = ET.SubElement(metadata, "column", **attr)
                if type(info["values"]) is dict:
                    valuesNode = ET.SubElement(column, "values")
                    for key, values in info["values"].items():
                        if type(values) is dict:
                            groupNode = ET.SubElement(valuesNode, "group", label=key.encode(self.encoding))
                            for key, value in values.items():
                                node = ET.SubElement(groupNode, "value", value=key)
                                node.text = ET.CDATA(value)
                        else:
                            node = ET.SubElement(valuesNode, "value", value=key)
                            node.text = ET.CDATA(value)
        if self.paginator:
            paginatorNode = ET.SubElement(table, "paginator")
            for k, v in self.paginator.items():
                paginatorNode.set(k, v)

        dataNode = ET.SubElement(table, "data")
        if rows:
            for row in rows:
                self.getRowXML(dataNode, row, customRowAttributes, encodeCustomAttributes)

        # exit(table)
        return ET.tostring(table)

    def getRowXML(self, parent, row, customRowAttributes, encodeCustomAttributes):
        rowNode = ET.SubElement(parent, "row", id=self._getRowField(row, "id"))
        if customRowAttributes:
            for name, field in row.items():
                if encodeCustomAttributes:
                    rowNode.set(name, base64.encodestring(self._getRowField(row, field)))
                else:
                    rowNode.set(name, self._getRowField(row, field))
        for name, info in self.columns.items():
            field = info['field']
            col = ET.SubElement(rowNode, "column")
            if self.writeColumnNames:
                col.set("name", name)
            text = self._getRowField(row, field)
            if type(text) is bool:
                text = "true" if text else "false"
            col.text = ET.CDATA(text)

    def renderXML(self, *arg):
        return self.getXML(*arg)

    def mapToArray(self, values):
        arr = []
        for k, v in values.items():
            if type(v) is dict:
                arr.append({"label": k, "value": self.mapToArray(v)})
            else:
                arr.append({"value": k, "label": v})
        return arr

    def getJSON(self, *params):
        # return (self.getPOJO(*params))
        return json.dumps(self.getPOJO(*params))

    def getPOJO(self, rows=False, customRowAttributes=False, encodeCustomAttributes=False, includeMetadata=True):
        results = {"data": []}
        if includeMetadata:
            results["metadata"] = []
            for name, info in self.columns.items():
                attr = {
                    "name": name,
                    "label": info["label"],
                    "datatype": info["type"],
                    "editable": info['editable'],
                    "bar": info['bar'],
                    "hidden": info['hidden'],
                    "values": self.mapToArray(info['values']) if type(info['values']) is dict else None
                }

                results["metadata"].append(attr)
        if self.paginator:
            results['paginator'] = self.paginator
        if rows:
            for row in rows:
                self.getRowPOJO(results["data"], row, customRowAttributes, encodeCustomAttributes)

        return results

    def getRowPOJO(self, parent, row, customRowAttributes, encodeCustomAttributes):
        data = {"id": self._getRowField(row, "id"), "values": {} if self.writeColumnNames else []}

        if customRowAttributes:
            for name, field in row.items():
                if encodeCustomAttributes:
                    data[name] = base64.encodestring(self._getRowField(row, field))
                else:
                    data[name] = self._getRowField(row, field)

        for name, info in self.columns.items():
            field = info['field']
            if self.writeColumnNames:
                data["values"][name] = self._getRowField(row, field)
            else:
                data["values"].append(self._getRowField(row, field))
        parent.append(data)


if __name__ == '__main__':
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
    with open("../demo.csv", "r", encoding='utf-8') as f:
        for line in f.readlines():
            row = line.split(";")
            if len(row) <= 1 or row[0] == 'id':
                continue
            if len(data) > 3:
                break
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
    # print(grid.getColumnFields())
    # print(grid.getColumnTypes())
    # print(grid.renderXML(data))
    # print(grid.getJSON(data))
    # print()
