''' SpreadsheettoJSON.py

This script is designed to produce a JSON file for use with the WAB Local Layer Widget
using values from an Excel table.
Utilizes openpyxl, available here: https://openpyxl.readthedocs.org/en/latest/
Tested using Python 3.4, might be backward compatible?
Torrin Hultgren, October 2015

********** Need to update popup configuration, community layers are not HUC 12s **********
'''
import sys, json, csv, openpyxl
import os

# This is the spreadsheet that contains all the content
rootpath = r"C:\inetpub\wwwroot\EnviroAtlas\scripts"
inputSpreadsheet = os.path.join(rootpath, r"EAWAB4JSON.xlsx")
# Just in case there are rows to ignore at the top - header is row 0
startingRow = 2
# This should be a csv table that maps spreadsheet column headers to json elements
# no great reason it needs to be in a standalone file rather than embedded in this
# script as a dictionary.
mapTablePath = os.path.join(rootpath, r"jsonfieldmap.csv")
# Output json file
outputFileName = os.path.join(rootpath, r"config.json")
errorLogFile = os.path.join(rootpath, r"errors.log")

popupDictionary = {"COMMUNITY" : "Block Group ID: {GEOID10}",
                   "NATIONAL" : "HUC 12 ID: {HUC_12}"}

# Empty rows cause python problems, remove them
def removeEmptyRows(rows):
    rowsToKeep = []
    for row in rows:
        rowEmpty = True
        for cell in row:
            if cell.value is not None:
                # If any non-null value in the row, flag this as a row to keep
                rowEmpty = False
                break
        if rowEmpty == False:
            rowsToKeep.append(str(cell.row))
    return rowsToKeep

def main(_argv):
    # Open the Excel spreadsheet
    inputWorkbook = openpyxl.load_workbook(filename = inputSpreadsheet,data_only=True)
    # Get the worksheet titled "EA_main"
    inputWorksheet = inputWorkbook["EA_main"]
    # Compile a dictionary of Spreadsheet field headers
    mapTable = open(mapTablePath)
    mapTableReader = csv.DictReader(mapTable,delimiter=',')
    mapDictionary = dict([(row['jsonElem'], row['Column']) for row in mapTableReader])

    # Create a dictionary of field titles to column letters
    fieldsToColumns = dict([(cell.value, cell.column) for cell in inputWorksheet.rows[0]])

    # Map the dictionary of csv titles to columns letters via the intermediate dictionary
    key = dict([(key, fieldsToColumns[mapDictionary[key]]) for key in mapDictionary.keys()])

    # Get row index numbers for non-empty rows:
    rowsToKeep = removeEmptyRows(inputWorksheet.rows[startingRow:])

    # Nothing is being piped to the error file right now
    validationErrors = open(errorLogFile,'w+')

    # Root structure of the JSON file
    fullJSON = {"layers": {"layer": []}}

    # Base map layer
    fullJSON["layers"]["layer"].append({
        "type": "Basemap",
        "name": "Topo Basemap",
        "layers": {
          "layer": [
            {
              "url": "http://services.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer",
              "isReference": "false",
              "opacity": 1
            }
          ]
        }
      })

    for rowID in rowsToKeep:
        name = inputWorksheet.cell(key["name"]+rowID).value
        layerJSON = {"opacity": 0.5,
                    "visible": "false"}
        if (inputWorksheet.cell(key["serviceType"]+rowID).value == "feature"):
            layerJSON["type"] ="FEATURE"
            layerJSON["autorefresh"] = 0
            layerJSON["mode"] = "ondemand"
            if inputWorksheet.cell(key["fieldName"]+rowID).value:
                layerJSON["popup"] = {
                  "title": popupDictionary[inputWorksheet.cell(key["eaScale"]+rowID).value],
                  "fieldInfos": [
                    {
                      "visible": "true"
                    }
                  ],
                  "showAttachments": "false"
                }
                layerJSON["popup"]["fieldInfos"][0]["fieldName"] = inputWorksheet.cell(key["fieldName"]+rowID).value
                layerJSON["popup"]["fieldInfos"][0]["label"] = name
        else:
            if (inputWorksheet.cell(key["serviceType"]+rowID).value == "dynamic" or inputWorksheet.cell(key["serviceType"]+rowID).value == "image"):
                layerJSON["type"] = "FEATURE"
            if (inputWorksheet.cell(key["serviceType"]+rowID).value == "tiled"):
                layerJSON["type"] = "FEATURE"
            ### code for reading in saved json files with layer/popup definitions.
            #with open(rootpath + inputWorksheet.cell(key["popupDefinition"]+rowID).value) as json_data:
            #    layerJSON["layers"] = json.load(json_data)
            ### the excel spreadsheet should include a relative path to a json file containing the layer/popup definition, which should be a JSON array of layer objects.
            ### will also need to add row: popupDefinition,popupDefinition (or corresponding human-friendly name for excel column to jsonfieldmap.csv to enable
        layerJSON["name"] = name
        layerJSON["url"] = inputWorksheet.cell(key["url"]+rowID).value

        stringList = ["eaID","eaScale","eaDescription","eaMetric","eaDfsLink","eaLyrNum","eaMetadata","eaBC","eaCA","eaCPW","eaCS","eaFFM","eaNHM","eaRCA","eaPBS","eaTopic","tileLink"]
        for elem in stringList:
            cell = inputWorksheet.cell(key[elem]+rowID)
            if elem == 'tileLink':
                if cell.value == 'yes':
                    cell = inputWorksheet.cell(key['tileURL']+rowID)
                    layerJSON[elem] = cell.value
            else:
                if cell.value != None:
                    cellValue = cell.value
                    if cellValue == 'x':
                        cellValue = 'true'
                    layerJSON[elem] = cellValue
        arrayList = [("eaTags",","),("eaBCSDD",";")]
        for elem,separator in arrayList:
             if inputWorksheet.cell(key[elem]+rowID).value:
                fullString = inputWorksheet.cell(key[elem]+rowID).value
                cleanString = fullString.strip(separator+' ')
                fullArray = cleanString.split(separator)
                cleanArray = [elemVal.strip() for elemVal in fullArray]
                layerJSON[elem] = cleanArray
        fullJSON["layers"]["layer"].append(layerJSON)

    validationErrors.close()
    outputFile = open(outputFileName,'w+')
    json.dump(fullJSON,outputFile,indent=4)
    outputFile.close()

if __name__ == "__main__":
    main(sys.argv)
