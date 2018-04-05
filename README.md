# KnoraJSONTestImport

The provided python script allows you to import JSON test data to Knora. JSON file content must follow the content required by the Knora API (POST v1/resources endpoint).

## Usage

`./ImportData.py <config.json> <data_folder>`

## config.json example

```json
{
  "url": "http://0.0.0.0:3333/",
  "email": "xxxx",
  "password": "xxxx"
}
```

## Data folder

Must contains one folder per class and one file per object. Folders and files are sorted in alphanumeric order to order import and to prevent object dependencies. IRI "link_value" will be resolved during import, set dependency to other objects as follow:

```json
{
        "link_value":
          "<%00.Image/002.json%>"
}
```

To associate an image to an object (StillImageRepresentation), image file must have the same name of the object file (supported extensions: .png and .jpg).

Data folder example (for LL ontology)

```unix
data
├── 00.Image          (Image class folder)
│   ├── 001.jpg       (Image related to data of 001.json)
│   ├── 001.json      (Image data of an object)
│   ├── 002.jpg
│   ├── 002.json
│   ├── 003.json
│   └── 003.png
└── 01.FreeContent    (FreeContent class folder)
    └── 001.json      (FreeContent data of an object)
```