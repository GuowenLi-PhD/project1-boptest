# -*- coding: utf-8 -*-
"""
This module implements the REST API used to interact with the test case.
The API is implemented using the ``flask`` package.

"""

# GENERAL PACKAGE IMPORT
# ----------------------
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import logging
import argparse


# LOGGING SETTING
# ----------------
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                    help="Provide logging level. Example --log DEBUG'")
log_level = parser.parse_args()
logging.basicConfig(level=log_level.logLevel)
error_number_input = "{} cannot be blank and it should be a number"
# ----------------

# TEST CASE IMPORT
# ----------------
from testcase import TestCase

# ----------------

# FLASK REQUIREMENTS
# ------------------
app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)


class InvalidUsage(Exception):
    """
        Custom exception for API.

    """
    
    def __init__(self, message, status_code=None, payload=None):
        """
            Constructor for custom error class.

                Parameters
                ----------
                message : str, error message.
                status_code : int, http status code.
                payload: None; payload.

        """
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Package error for information."""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        if self.status_code is not None:
            rv['status_code'] = self.status_code
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """
    Register error handler with API.

        Parameters
        ----------
        error : obj, instance of error.

    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


# ------------------

# INSTANTIATE TEST CASE
# ---------------------
try:
    case = TestCase()
except Exception as ex:
    message = "Failed to instantiate the fmu: {}".format(ex)
    app.logger.error(message)
    raise InvalidUsage(message, status_code=500)
# ---------------------

# DEFINE ARGUMENT PARSERS
# -----------------------
# ``step`` interface
parser_step = reqparse.RequestParser()
parser_step.add_argument('step',type=float,required=True,help=error_number_input.format('step'))
# ``initialize`` interface
parser_initialize = reqparse.RequestParser()
parser_initialize.add_argument('start_time',type=float,required=True,help=error_number_input.format('start time'))
parser_initialize.add_argument('warmup_period',type=float,required=True,help=error_number_input.format('warmup period'))
# ``advance`` interface
parser_advance = reqparse.RequestParser()
for key in case.u.keys():
    parser_advance.add_argument(key)
# ``forecast_parameters`` interface
parser_forecast_parameters = reqparse.RequestParser()
forecast_parameters = ['horizon', 'interval']
for arg in forecast_parameters:
    parser_forecast_parameters.add_argument(arg,type=float,required=True,help=error_number_input.format(arg))
# ``price_scenario`` interface
parser_scenario = reqparse.RequestParser()
parser_scenario.add_argument('electricity_price',type=str,help="invalid price")
parser_scenario.add_argument('time_period',type=str,help="invalid time preriod")
# ``results`` interface
results_var = reqparse.RequestParser()
results_var.add_argument('point_name',type=str,required=True,help="point name cannot be blank")
results_var.add_argument('start_time',type=float,required=True,help=error_number_input.format('start time'))
results_var.add_argument('final_time',type=float,required=True,help=error_number_input.format('final time'))
import traceback
# -----------------------

# DEFINE REST REQUESTS
# --------------------


class Advance(Resource):
    '''Interface to advance the test case simulation.'''

    def post(self):
        '''POST request with input data to advance the simulation one step
        and receive current measurements.'''
        u = parser_advance.parse_args()
        app.logger.info("Receiving a new advance request: {}".format(u))        
        result = case.advance(u)
        if not isinstance(result, str):
            app.logger.info("Advanced the simulation")
            return result, 200
        else:
            msg = "Fail to advanced the simulation: {}".format(result)
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)



class Initialize(Resource):
    '''Interface to initialize the test case simulation.'''

    def put(self):
        '''PUT request to initialize the test.'''
        args = parser_initialize.parse_args()
        app.logger.info("Receiving a new initialize request: {}".format(args))
        start_time = float(args['start_time'])
        warmup_period = float(args['warmup_period']) 
        result = case.initialize(start_time, warmup_period)        
        if not isinstance(result, str):
            app.logger.info("Initialized the simulation")
            return result, 200
        else:
            msg = "Fail to initialize the simulation: {}".format(result)
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)



class Step(Resource):
    '''Interface to test case simulation step size.'''

    def get(self):
        '''GET request to receive current simulation step in seconds.'''
        app.logger.info("Receiving a new query for step")
        try:
            step = case.get_step()
        except:
            msg = "Fail to return the simulation step:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)
        return step, 200

    def put(self):
        '''PUT request to set simulation step in seconds.'''
        args = parser_step.parse_args()
        app.logger.info("Receiving a new set step request: {}".format(args))
        step = args['step']
        try:
            step = case.set_step(step)
        except:
            msg = "Fail to set the simulation step:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)
        return step, 200


class Inputs(Resource):
    '''Interface to test case inputs.'''

    def get(self):
        '''GET request to receive list of available inputs.'''
        app.logger.info("Receiving a new query for input list")
        try:
            u_list = case.get_inputs()
        except:
            msg = "Fail to return the inputs:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)
        return u_list, 200


class Measurements(Resource):
    '''Interface to test case measurements.'''

    def get(self):
        '''GET request to receive list of available measurements.'''
        app.logger.info("Receiving a new query for output list")
        try:
            y_list = case.get_measurements()
        except:
            msg = "Fail to return the outputs:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)
        return y_list, 200


class Results(Resource):
    '''Interface to test case result data.'''

    def put(self):
        '''GET request to receive measurement data.'''
        app.logger.info("Receiving a new query for results")  
        args = results_var.parse_args(strict=True) 
        var = args['point_name']
        start_time = float(args['start_time'])
        final_time = float(args['final_time'])        
        try:
            Y = case.get_results(var, start_time, final_time)
            for key in Y:
                  Y[key] = Y[key].tolist()
        except:
            msg = "Fail to return the results:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)
        return Y, 200


class KPI(Resource):
    '''Interface to test case KPIs.'''

    def get(self):
        '''GET request to receive KPI data.'''
        app.logger.info("Receiving a new query for KPI")
        try:
            kpi = case.get_kpis()
        except:
            msg = "Fail to return the KPI:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)
        return kpi, 200


class Forecast_Parameters(Resource):
    '''Interface to test case forecast parameters.'''

    def get(self):
        '''GET request to receive forecast parameters.'''
        app.logger.info("Receiving a new query for forecast parameters")
        try:
            forecast_parameters = case.get_forecast_parameters()
        except:
            msg = "Fail to return the forecast parameters:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)
        return forecast_parameters, 200

    def put(self):
        '''PUT request to set forecast horizon and interval inseconds.'''    
        args = parser_forecast_parameters.parse_args()
        app.logger.info("Receiving a new request for setting the forecast: ()".format(args))           
        horizon = args['horizon']
        interval = args['interval']
        try:
            result = case.set_forecast_parameters(horizon, interval)
        except:
            msg = "Fail to return the KPI:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)
        forecast_parameters = case.get_forecast_parameters()
        return forecast_parameters, 200


class Forecast(Resource):
    '''Interface to test case forecast data.'''

    def get(self):
        '''GET request to receive forecast data.'''
        app.logger.info("Receiving a new query for forecast")
        try:
            forecast = case.get_forecast()
        except:
            msg = "Fail to return the forecast:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)
        return forecast, 200


class Scenario(Resource):
    '''Interface to test case scenario.'''

    def get(self):
        '''GET request to receive current scenario.'''
        app.logger.info("Receiving a new query for scenario")
        try:        
            scenario = case.get_scenario()
        except:
            msg = "Fail to return the scenario:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)
        return scenario, 200

    def put(self):
        '''PUT request to set scenario.'''          
        scenario = parser_scenario.parse_args(strict=True)
        app.logger.info("Receiving a new request for setting the scenario: {}".format(scenario)) 
        try:        
            result = case.set_scenario(scenario)
        except:
            msg = "Fail to set the scenario:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)
        return result, 200


class Name(Resource):
    '''Interface to test case name.'''

    def get(self):
        '''GET request to receive test case name.'''
        app.logger.info("Receiving a new query for case name")
        try:
            name = case.get_name()
        except:
            msg = "Fail to return the case name:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)
        return  name, 200


class Version(Resource):
    '''Interface to BOPTEST version.'''

    def get(self):
        try:
            version = case.get_version()
        except:
            msg = "Fail to return the case name:{}".format(traceback.format_exc())
            app.logger.error(msg)
            raise InvalidUsage(msg, status_code=500)

        return version, 200

    # --------------------


# ADD REQUESTS TO API WITH URL EXTENSION
# --------------------------------------
api.add_resource(Advance, '/advance')
api.add_resource(Initialize, '/initialize')
api.add_resource(Step, '/step')
api.add_resource(Inputs, '/inputs')
api.add_resource(Measurements, '/measurements')
api.add_resource(Results, '/results')
api.add_resource(KPI, '/kpi')
api.add_resource(Forecast_Parameters, '/forecast_parameters')
api.add_resource(Forecast, '/forecast')
api.add_resource(Scenario, '/scenario')
api.add_resource(Name, '/name')
api.add_resource(Version, '/version')
# --------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
