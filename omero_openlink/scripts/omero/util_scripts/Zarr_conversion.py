#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script can be used with python 3.6 or higher

This script creates a job file for zarr conversions with parameters according the specification for ZARR_PARAMS.
Structure of job file:
{
    "DataType":,
    "IDs":,
    UserID:,
    UserName:,
    ActionDate:,
    Email:,
    Parameter:{...}
}
@author Susanne Kunis
<a href="mailto:sinukesus@gmail.com">sinukesus@gmail.com"</a>
"""

import os
import omero
from omero.rtypes import rstring, rlong
import omero.scripts as scripts
from omero.gateway import BlitzGateway

import datetime
import json

# --------------- Configuration ---------------------------
# directory for jobfile
JOB_DIR = "/opt/omero/server/adminUtil/Jobs/ZarrConversion"

CONVERSION_TOOL = "bioformats2raw"
# define name:, is optional parameter:, desc:, default value
# config for bioformats2raw (see https://github.com/glencoesoftware/bioformats2raw/blob/master/src/main/java/com/glencoesoftware/bioformats2raw/Converter.java)
ZARR_PARAMS = [
    ['Min_XY_size', 'True', 'Specifies the desired size for the largest XY dimension of the smallest resolution.', '256'],
    ['Chunk_Y', 'False', 'Maximum tile height', "1024"],
    ['Chunk_X', 'False', 'Maximum tile width', "1024"],
    ['Chunk_Z', 'False', 'Maximum chunk depth to read', "1"],
    ['Resolution', 'True', 'Number of pyramid resolutions to generate', "null"],
    ['downsample_type', 'False', 'Tile downsampling algorithm', 'SIMPLE'],
    ['compression','False','Compression type for Zarr','blosc'],
    ['no_nested','False','Whether to use "/" as the chunk path separator','False']
]
# ------------------------------------------
# OMERO.script GUI elements
PARAM_DATATYPE = "Data_Type"
PARAM_ID = "IDs"
PARAM_MAIL = "Email"

# additional jobfile elements
Y_USERID = "UserID"
Y_USERNAME = "UserName"
Y_DATE = "ActionDate"
Y_ZARR_PARAMS = "Parameter"

class ScriptElement:
    def __init__(self, elem):
        self._name = elem[0]
        self._opt = elem[1]
        self._desc = elem[2] + f" Default: {elem[3]}"
        self._defaultVal = elem[3]
    def createInput(self,grouping):
        return scripts.String(self._name,optional=self._opt,grouping=grouping,
        description=self._desc,default=self._defaultVal,)


def create_jobfile(subject_job,data):
    timestamp = data[Y_DATE]
    fileName = f"{timestamp}_{subject_job}.json"
    filePath = os.path.join(JOB_DIR,fileName)

    with open(filePath,'w',encoding='utf-8') as file:
        json.dump(data,file,ensure_ascii=False, indent=4)
        file.flush()

    message = f"Jobfile {fileName} created. You will receive a notification as soon as the conversion is complete."
    return message



def createData_dict(params,conn):
    data = {}
    try:
        data[PARAM_DATATYPE] = params.get(PARAM_DATATYPE)
        data[PARAM_ID] = params.get(PARAM_ID)
        data[Y_USERID] = conn.getUser().getId()
        data[Y_USERNAME] = conn.getUser().getName()
        date = datetime.datetime.now()
        timeStr = date.strftime("%Y-%m-%dT%H-%M-%S")
        data[Y_DATE] = timeStr

        data[PARAM_MAIL] = params.get(PARAM_MAIL)

        zarr_params={}
        for elem in ZARR_PARAMS:
            zarr_params[elem[0]] = params.get(elem[0])
            
        data[Y_ZARR_PARAMS] = zarr_params
        
    except Exception as e:
        message = "Error while reading out GUI parameter." + str(e)

    return "Dict created successfully.",data

def run(conn, params):
    message = ""
    message, data = createData_dict(params, conn)

    if "Error" in message:
        return message

    subject = f"{conn.getUser().getName()}_{conn.getUser().getId()}"
    
    try: 
        message = create_jobfile(subject,data)
    except Exception as e:
        message = ("Error while creating jobfile! Please contact your OMERO administrator!")
        
    return message

def run_script():
    """
    The main entry point of the script, as called by the client via the
    scripting service, passing the required parameters.
    """
    # predefinitions for GUI parameter
    dataTypes = [
        rstring("Screen"),
        rstring("Plate"),
        rstring("Project"),
        rstring("Dataset"),
        rstring("Image"),
    ]

    client = omero.client()
    client.createSession()
    conn = omero.gateway.BlitzGateway(client_obj=client)
    conn.SERVICE_OPTS.setOmeroGroup(-1)
    dic = conn.getUser().simpleMarshal()
    userEmail = ""
    if "email" in dic and dic["email"]:
        userEmail = dic["email"]
    
    client.closeSession()

    
    script_params = omero.grid.JobParams()
    script_params.name = "Zarr conversion"
    script_params.description = """
    This script creates a job file for zarr conversions with parameters according the specification for {}.
    You will receive a notification via email as soon as the conversion is complete.
    """.format(CONVERSION_TOOL)
    script_params.inputs = {} 
    
    script_params.inputs[PARAM_DATATYPE] = scripts.String(
            PARAM_DATATYPE,
            optional=False,
            grouping="1",
            description="Choose source of objects",
            values=dataTypes,
        )
    script_params.inputs[PARAM_ID] = scripts.List(
            PARAM_ID,
            optional=False,
            grouping="2",
            description="List of Image IDs to process",
        ).ofType(rlong(0))

    script_params.inputs[PARAM_MAIL] = scripts.String(
        PARAM_MAIL,
        optional=False,
        grouping="3",
        description="email for notification (if not stated in user settings)",
        default=userEmail,
        )

    # add zarr conversion parameter as defined
    maingrouping = "4"
    counter = 1
    
    for elem in ZARR_PARAMS:
        pElem = ScriptElement(elem)
        gr = maingrouping + "." + str(counter)
        script_params.inputs[pElem._name] = pElem.createInput(gr)
        counter = counter+1
    
    script_params.namespaces = [omero.constants.namespaces.NSDYNAMIC]
    script_paramsversion = "1.0.0"
    script_params.authors = ["Susanne Kunis", "CellNanOs"]
    script_params.institutions = ["University of Osnabrueck"]
    script_params.contact = "sinukesus@gmail.com"
    
    
    client = scripts.client(script_params)

    try:
        params = client.getInputs(unwrap=True)
        conn = BlitzGateway(client_obj=client)
        message = run(conn,params)
        if "Error" in message:
            client.setOutput("Error",rstring(message))
        else:
            client.setOutput("Message", rstring(message))
    finally:
        client.closeSession()


if __name__ == "__main__":
    run_script()