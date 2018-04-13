# KnoraJSONTestImport

The provided python script allows you to import JSON test data to Knora. JSON file content must follow the content required by the Knora API (POST v1/resources and v1/values endpoints).

## Requirements: Python 3 + requests

A clean and stable way is to create an env for python3 with required packages:

```unix
$ python3 -m venv python3-env
$ source python3-env/bin/activate
$ python --version
Python 3.6.4
$ pip install requests
$ ./ImportData.py
Usage: ImportData.py <connection.json> <data.list>
$ deactivate
```

## Usage

You need to provide a connection file and data description file:

`Usage: ImportData.py <connection.json> <data.list>`

### Connection file

connection.json example:

```json
{
  "url": "http://0.0.0.0:3333/",
  "email": "xxxx",
  "password": "xxxx"
}
```

### Data description file

The data file must describe operations (CREATE or UPDATE) to launch in 
the specified order (empty or # lines will be ignored):

```json
# Data list for LL model test

CREATE Image
CREATE FreeContent
UPDATE FreeContent_Image
```

The first term provides the operation, the second one is the folder containing 
json data files to use (filenames are loaded using alphanumeric order).
The folder path must be relative to the data.file location.

To set a `link_value`, you can use resolver during import, set dependency to 
other objects as follow:

See in `FreeContent/home.json`:
```json
"http://www.knora.org/ontology/0113/lumieres-lausanne#hasAdditionalResource": [
      {
        "link_value":
          "<%Image/MHL122991_-_copie.json%>"
      }
    ],
```
`<%Image/MHL122991_-_copie.json%>` will be replaced by the IRI of the previously 
created object of file `MHL122991_-_copie.json`.

Same way to update a link and find the current object to update (`"res_id"`), 
see in `FreContent_Image/home_update.json`:
```json
{
  "link_value": "<%Image/Trouvaille_LL_5_Luca_Delachaux_accueil.json%>",
  "res_id": "<%FreeContent/home.json%>",
  "prop":
    "http://www.knora.org/ontology/0113/lumieres-lausanne#hasAdditionalResource",
  "project_id": "http://rdfh.ch/projects/0113"
}
```

To associate an image (will be store in Sipi) to an object (subclass of
`StillImageRepresentation`), the image file must have the same name of the
object file (supported extensions: .png and .jpg).

Data folder example of LL ontology:

```unix
── FreeContent
│   └── home.json
├── FreeContent_Image
│   └── home.json
├── Image
│   ├── MHL122991_-_copie.jpg
│   ├── MHL122991_-_copie.json
│   ├── Trouvaille_LL_5_Luca_Delachaux_accueil.jpg
│   └── Trouvaille_LL_5_Luca_Delachaux_accueil.json
└── data.list
```

## Test

Having a Knora stack correctly configured for Lumières.Lausanne project:

```unix
$ ./ImportData.py connection.json data/data.list

- Load config file: /Users/gfaucher/work/projects/lumieres/LL2018/data-test/connection.json
   * url=http://0.0.0.0:3333 email=lumieres@unil.ch password=test

- Create data source from data list: /Users/gfaucher/work/projects/lumieres/KnoraJSONTestImport/data/data.list

- Load data source (nb operations: 4)

	-> 1/4 Create Image/MHL122991_-_copie.json
		-> Related image : image/jpeg /Users/gfaucher/work/projects/lumieres/KnoraJSONTestImport/data/Image/MHL122991_-_copie.jpg
		-> IRI: http://rdfh.ch/0113/lumieres-lausanne/U0lbpjj4RIGs3JAEveK2ug

	-> 2/4 Create Image/Trouvaille_LL_5_Luca_Delachaux_accueil.json
		-> Related image : image/jpeg /Users/gfaucher/work/projects/lumieres/KnoraJSONTestImport/data/Image/Trouvaille_LL_5_Luca_Delachaux_accueil.jpg
		-> IRI: http://rdfh.ch/0113/lumieres-lausanne/voVKvBE1THys--vqgTMgew

	-> 3/4 Create FreeContent/home.json
		-> resolved link Image/MHL122991_-_copie.json into http://rdfh.ch/0113/lumieres-lausanne/U0lbpjj4RIGs3JAEveK2ug
		-> IRI: http://rdfh.ch/0113/lumieres-lausanne/WMDKmCj0SzuKMfIrDrW7mg

	-> 4/4 Update FreeContent_Image/home_update.json
		-> resolved link Image/Trouvaille_LL_5_Luca_Delachaux_accueil.json into http://rdfh.ch/0113/lumieres-lausanne/voVKvBE1THys--vqgTMgew
		-> resolved link FreeContent/home.json into http://rdfh.ch/0113/lumieres-lausanne/WMDKmCj0SzuKMfIrDrW7mg

- Done: created 3 and updated 1 objects, added 2 images [3.035555839538574 s]

```
