# -*- coding: utf-8 -*-
"""
This module runs tests for the Data Generator and Data Manager. The data
generator requires as an input an fmu path where the data is to be stored
such that it can be loaded into a test case afterwards. On the other hand, 
the data manager requires a test case as an input such that it can load
and retrieve the data into the test case and from its fmu. 
testcase2 is used to test the Data Generator and Data Manager. testcase3
is used to test the Data Manager in a multi-zone building example. 

"""

import unittest
import os
import shutil
import pandas as pd
import numpy as np
import utilities
import json
import testcase
from data.data_generator import Data_Generator
from data.data_manager import Data_Manager

testing_root_dir = os.path.join(utilities.get_root_path(), 'testing')

class DataGeneratorTest(unittest.TestCase, utilities.partialChecks):
    '''Tests the data generator class
    
    '''
    
    def setUp(self):
        '''Setup for each test.
        
        '''
        
        resources_dir = os.path.join(utilities.get_root_path(),'testcases','testcase2','models','Resources')
        self.gen = Data_Generator(resources_dir)
         
    def test_generate_weather(self):
        '''Runs the generate weather data method and compares
        trajectories with references.
           
        '''
           
        # Generate weather file
        self.gen.generate_weather()
        os.chdir(testing_root_dir)
        # Set generated file path
        gen_filepath = os.path.join(self.gen.resources_dir, 
                                    'weather.csv')
           
        # Set reference file path
        ref_filepath = os.path.join(testing_root_dir, 
            'references', 'data', 'testcase2', 'default_weather.csv')
          
        # Check the data file has been created
        self.assertTrue(os.path.exists(gen_filepath))
          
        # Read data into data frame
        df_gen = pd.read_csv(gen_filepath).set_index('time')
          
        # Check trajectories 
        self.compare_ref_timeseries_df(df_gen, ref_filepath)
         
    def test_generate_prices(self):
        '''Runs the generate prices method and compares trajectories 
        with references.
        
        '''
        
        # Generate weather file
        self.gen.generate_prices()
        
        # Set generated file path
        gen_filepath = os.path.join(self.gen.resources_dir,
                                    'prices.csv')
        
        # Set reference file path
        ref_filepath = os.path.join(testing_root_dir,
            'references', 'data', 'testcase2', 'default_prices.csv')
        
        # Check the data file has been created
        self.assertTrue(os.path.exists(gen_filepath))
        
        # Read data into data frame
        df_gen = pd.read_csv(gen_filepath).set_index('time')
        
        # Check trajectories 
        self.compare_ref_timeseries_df(df_gen, ref_filepath)      
        
    def test_generate_emissions(self):
        '''Runs the generate emissions method and compares 
        trajectories with references.
        
        '''
        
        # Generate weather file
        self.gen.generate_emissions()
        
        # Set generated file path
        gen_filepath = os.path.join(self.gen.resources_dir,
                                    'emissions.csv')
        
        # Set reference file path
        ref_filepath = os.path.join(testing_root_dir, 
            'references', 'data', 'testcase2', 'default_emissions.csv')
        
        # Check the data file has been created
        self.assertTrue(os.path.exists(gen_filepath))
        
        # Read data into data frame
        df_gen = pd.read_csv(gen_filepath).set_index('time')
        
        # Check trajectories 
        self.compare_ref_timeseries_df(df_gen, ref_filepath)

    def test_generate_occupancy(self):
        '''Runs the generate occupancy method and compares 
        trajectories with references.
        
        '''
        
        # Generate weather file
        self.gen.generate_occupancy(occ_num=10)
        
        # Set generated file path
        gen_filepath = os.path.join(self.gen.resources_dir,
                                    'occupancy.csv')
        
        # Set reference file path
        ref_filepath = os.path.join(testing_root_dir, 
            'references', 'data', 'testcase2', 'default_occupancy.csv')
        
        # Check the data file has been created
        self.assertTrue(os.path.exists(gen_filepath))
        
        # Read data into data frame
        df_gen = pd.read_csv(gen_filepath).set_index('time')
        
        # Check trajectories 
        self.compare_ref_timeseries_df(df_gen, ref_filepath)
        
    def test_generate_internalGains(self):
        '''Runs the generate internal gains method and compares 
        trajectories with references.
        
        '''
        
        # Generate weather file
        self.gen.generate_internalGains()
        
        # Set generated file path
        gen_filepath = os.path.join(self.gen.resources_dir,
                                    'internalGains.csv')
        
        # Set reference file path
        ref_filepath = os.path.join(testing_root_dir, 
            'references', 'data', 'testcase2', 'default_internalGains.csv')
        
        # Check the data file has been created
        self.assertTrue(os.path.exists(gen_filepath))
        
        # Read data into data frame
        df_gen = pd.read_csv(gen_filepath).set_index('time')
        
        # Check trajectories 
        self.compare_ref_timeseries_df(df_gen, ref_filepath)
        
    def test_generate_setpoints(self):
        '''Runs the generate setpoints method for testcase 2 and 
        compares trajectories with references.
        
        '''
        
        # Generate weather file
        self.gen.generate_setpoints()
        
        # Set generated file path
        gen_filepath = os.path.join(self.gen.resources_dir,
                                    'setpoints.csv')
        
        # Set reference file path
        ref_filepath = os.path.join(testing_root_dir, 
            'references', 'data', 'testcase2', 'default_setpoints.csv')
        
        # Check the data file has been created
        self.assertTrue(os.path.exists(gen_filepath))
        
        # Read data into data frame
        df_gen = pd.read_csv(gen_filepath).set_index('time')
        
        # Check trajectories 
        self.compare_ref_timeseries_df(df_gen, ref_filepath)   
                     
class PartialDataManagerTest(object):
    '''This partial class implements common tests for the data manager class.
       
    References to self attributes for the tests should be set in the setUp 
    method of the particular testclass test.  They are:

    man : Data_Manager
        A Data_Manager instance pointing to a deployed testcase.
    case : TestCase
        A deployed TestCase object
    ref_kpis : path
        Path to reference with the kpis loaded to the test case.
    ref_data_loaded : path
        Path to reference with the data loaded to the test case.
    ref_data_default : path
        Path to reference with the data retrieved from the test case.
    ref_data_index : path
        Path to reference with the data retrieved from the test case
        with specified interval parameters.
            
    '''
             
    def test_save_data_and_kpisjson(self):
        '''Check if the data manager can store data and the kpis.json 
        file within the fmu
         
        '''
        
        self.man.save_data_and_kpisjson(fmu_path=self.case.fmupath)
         
        files_in_fmu = []
        for f in self.man.z_fmu.infolist():
            files_in_fmu.append(f.filename)
         
        self.assertTrue('resources/weather.csv' in files_in_fmu)
        self.assertTrue('resources/prices.csv' in files_in_fmu)
        self.assertTrue('resources/emissions.csv' in files_in_fmu)
        self.assertTrue('resources/occupancy.csv' in files_in_fmu)
        self.assertTrue('resources/internalGains.csv' in files_in_fmu)
        self.assertTrue('resources/setpoints.csv' in files_in_fmu)
        self.assertTrue('resources/kpis.json' in files_in_fmu)
     
    def test_load_data_and_kpisjson(self):
        '''Check if the data manager can load the data and the kpis.json 
        file into a test case 
          
        '''
        
        # Load the data into the test case
        self.man.load_data_and_kpisjson()
         
        # Check if test case has kpi_json and data attributes
        self.assertTrue(hasattr(self.case, 'kpi_json'))
        self.assertTrue(hasattr(self.case, 'data'))
        
        # Check content of the kpis.json loaded
        with open(os.path.join(self.ref_kpis),'r') as f:
            kpi_json_ref = json.loads(f.read()) 
        self.assertDictEqual(self.case.kpi_json, kpi_json_ref)
        
        # Check the content of the data loaded
        df_man = self.case.data
        self.compare_ref_timeseries_df(df_man, self.ref_data_loaded)

    def test_get_data_default(self):
        '''Check that the data manager can retrieve the test case data
        for the default horizon and interval.
         
        '''       
        
        # Get the data
        data_dict = self.man.get_data()
        
        # Check the data retrieved with the manager
        df_man = pd.DataFrame(data_dict).set_index('time')
        self.compare_ref_timeseries_df(df_man, self.ref_data_default)
     
    def test_get_data_index(self):
        '''Check that the data manager can retrieve the test case data
        when an arbitrary time index is provided.
         
        '''       
        
        # Define index
        index = np.arange(0, 7*24*3600, 321)
         
        # Get the data
        data_dict = self.man.get_data(index=index)
        
        # Check the data retrieved with the manager
        df_man = pd.DataFrame(data_dict).set_index('time')
        self.compare_ref_timeseries_df(df_man, self.ref_data_index)
    
class DataManagerSingleZoneTest(unittest.TestCase, utilities.partialChecks,
                      PartialDataManagerTest):
    '''Tests the data manager class in a single-zone example. 
     
    '''
 
    def setUp(self):
        '''Setup for each test.
         
        '''
        
        # mimic BOPTEST setup
        testcase2_dir = os.path.join(utilities.get_root_path(),'testcases', 'testcase2')
        os.mkdir(os.path.join(utilities.get_root_path(),'models'))
        shutil.copyfile(os.path.join(testcase2_dir,'models', 'wrapped.fmu'),
                        os.path.join(utilities.get_root_path(),'models', 'wrapped.fmu'))
        shutil.copyfile(os.path.join(testcase2_dir,'config.json'),
                        os.path.join(utilities.get_root_path(),'config.json'))
        os.chdir(utilities.get_root_path())
        self.case=testcase.TestCase()
        
        # Instantiate a data manager
        self.man = self.case.data_manager

        # Set reference file paths
        self.ref_kpis = os.path.join(testing_root_dir, 
            'references', 'data', 'testcase2', 'kpis.json')
        self.ref_data_loaded = os.path.join(testing_root_dir, 
            'references', 'data', 'testcase2', 'tc2_data_loaded.csv')
        self.ref_data_default = os.path.join(testing_root_dir,
            'references', 'data', 'testcase2', 'tc2_data_retrieved_default.csv')
        self.ref_data_index = os.path.join(testing_root_dir,
            'references', 'data', 'testcase2', 'tc2_data_retrieved_index.csv')     
        
    def tearDown(self):
        '''Teardown for each test.
        
        '''
        
        # Delete leftover files
        shutil.rmtree(os.path.join(utilities.get_root_path(),'models'))
        os.remove(os.path.join(utilities.get_root_path(),'config.json'))
        del(self.case)
    
class DataManagerMultiZoneTest(unittest.TestCase, utilities.partialChecks,
                               PartialDataManagerTest):
    '''Tests the data manager class in a single-zone example.  
     
    '''
 
    def setUp(self):
        '''Setup for each test.
         
        '''
        
        # mimic BOPTEST setup
        testcase3_dir = os.path.join(utilities.get_root_path(),'testcases', 'testcase3')
        os.mkdir(os.path.join(utilities.get_root_path(),'models'))
        shutil.copyfile(os.path.join(testcase3_dir,'models', 'wrapped.fmu'),
                        os.path.join(utilities.get_root_path(),'models', 'wrapped.fmu'))
        shutil.copyfile(os.path.join(testcase3_dir,'config.json'),
                        os.path.join(utilities.get_root_path(),'config.json'))
        os.chdir(utilities.get_root_path())
        self.case=testcase.TestCase()
        
        # Instantiate a data manager
        self.man = self.case.data_manager

        # Set reference file paths
        self.ref_kpis = os.path.join(testing_root_dir, 
            'references', 'data', 'testcase3', 'kpis.json')
        self.ref_data_loaded = os.path.join(testing_root_dir, 
            'references', 'data', 'testcase3', 'tc3_data_loaded.csv')
        self.ref_data_default = os.path.join(testing_root_dir,
            'references', 'data', 'testcase3', 'tc3_data_retrieved_default.csv')
        self.ref_data_index = os.path.join(testing_root_dir,
            'references', 'data', 'testcase3', 'tc3_data_retrieved_index.csv')

    def tearDown(self):
        '''Teardown for each test.
        
        '''
        
        # Delete leftover files
        shutil.rmtree(os.path.join(utilities.get_root_path(),'models'))
        os.remove(os.path.join(utilities.get_root_path(),'config.json'))
        del(self.case)
        
if __name__ == '__main__':
    utilities.run_tests(os.path.basename(__file__))