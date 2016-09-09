# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 10:17:30 2015

@author: ebachelet
"""

###############################################################################

# General code manager

###############################################################################

import os
import time

import matplotlib.pyplot as plt

import numpy as np

from pyLIMA import event
from pyLIMA import telescopes
from pyLIMA import microlmodels


def main(command_line):
    events_names = [event_name for event_name in os.listdir(command_line.input_directory) if
                    ('OGLE' in event_name) and ('Follow' not in event_name)]
    events_names2 = [event_name for event_name in os.listdir(command_line.input_directory) if
                     ('.dat' in event_name) and ('~' not in event_name)]

    start = time.time()
    results = []
    errors = []

    for event_name in events_names[0:]:

        # name='Lightcurve_'+str(17)+'_'
        name = 'OB160795'
        # name = 'Lightcurve_9_'
        current_event = event.Event()
        current_event.name = name

        event_telescopes = [i for i in events_names2]
        # event_telescopes = ['OGLE-2016-BLG-0676.dat','MOA-2016-BLG-215_MOA_transformed.dat',
        # 'MOA-2016-BLG-215_transformed.dat']
        # event_telescopes = ['MOA-2016-BLG-215_transformed.dat']
        # Names = ['OGLE','Kepler']
        # Locations = ['Earth','Space']

        current_event.ra = 271.0010
        current_event.dec = -28.15511
        Names = ['Survey', 'Follow']
        Locations = ['Earth', 'Space']
        # event_telescopes = ['Lightcurve_1_Survey.dat','Lightcurve_1_Follow.dat']
        # event_telescopes = ['MOA2016BLG0221_flux.dat','MOA2016BLG0221_K2_flux.dat']
        # event_telescopes = ['MOA2016BLG0233_flux.dat','MOA2016BLG0233_K2_flux.dat']
        # event_telescopes = ['OGLE2016BLG0548.dat','OGLE20160548_K2_flux.dat']
        # event_telescopes = ['MOA2016BLG0286_flux.dat']
        # event_telescopes = ['MOA2016BLG0307_flux.dat']
        count = 0
        import pdb;
        pdb.set_trace()
        start = time.time()
        for event_telescope in event_telescopes:
            try:
                raw_light_curve = np.genfromtxt(command_line.input_directory + event_telescope,
                                                usecols=(0, 1, 2))
                # good = np.where(raw_light_curve[:,1]<24)[0]
                # good = np.where(raw_light_curve[:, 0] > -1)[0]
                # raw_light_curve = raw_light_curve[good]

                if 'COJA' in event_telescope:
                    raw_light_curve = np.genfromtxt(command_line.input_directory + event_telescope,
                                                    usecols=(0,2, 3))
                    #raw_light_curve = np.array(
                    #[raw_light_curve[:, 2], raw_light_curve[:, 0], raw_light_curve[:, 1]]).T
                lightcurve = np.array(
                    [raw_light_curve[:, 0], raw_light_curve[:, 1], raw_light_curve[:, 2]]).T

                if lightcurve[0, 0] < 2450000:
                    lightcurve[:, 0] += 2450000

            except:
                raw_light_curve = np.genfromtxt(command_line.input_directory + event_telescope,
                                                usecols=(0, 1))
                #noise = 7.5*(raw_light_curve[:,1]+1000)**0.5
                noise = 0.3*(raw_light_curve[:,1]+200)
                raw_light_curve = np.c_[raw_light_curve,noise]

            if (event_telescope[:-4] == 'Kepler_R'):

                # good =  np.where(lightcurve[:,1]>-22181.96)[0]
                # lightcurve = lightcurve[good]
                # lightcurve[:,2] = lightcurve[:,2]*4.3
                lightcurve = np.array(
                    [raw_light_curve[:, 0], raw_light_curve[:, 1], raw_light_curve[:, 2]]).T
                telescope = telescopes.Telescope(name='Kepler', camera_filter=event_telescope[-5],
                                                 light_curve_flux=lightcurve,
                                                 light_curve_flux_dictionnary={'time': 0, 'flux': 1, 'err_flux': 2},reference_flux = 200)
                telescope.location = 'Space'

            else:
                # if lightcurve[0,0] <2450000:
                # lightcurve[:,2] = lightcurve[:, 2] + 2450000
                # lightcurve[:, 2] = lightcurve[:, 2] * 1.8
                telescope = telescopes.Telescope(name=event_telescope[0:-4], camera_filter=event_telescope[-5],
                                                 light_curve_magnitude=lightcurve,
                                                 light_curve_magnitude_dictionnary={'time': 0, 'mag': 1, 'err_mag': 2})
                telescope.location = 'Earth'

            telescope.gamma = 0.5
            current_event.telescopes.append(telescope)
            count += 1

        print 'Start;', current_event.name

        current_event.find_survey('OGLE_I')
        # current_event.check_event()

        # Model = microlmodels.MLModels(current_event, command_line.model,
        #                              parallax=['None', 50.0])

        Model = microlmodels.create_model('PSPL', current_event, parallax=['Annual', 2457512])
        Model.parameters_guess = [2457512, 0.142,4,0,0]
        # Model.parameters_boundaries[3] = (-5.0, -1.0)

        # Model.fancy_to_pyLIMA_dictionnary = {'logrho': 'rho'}
        # Model.pyLIMA_to_fancy = {'logrho': lambda parameters: np.log10(parameters.rho)}

        # Model.fancy_to_pyLIMA = {'rho': lambda parameters: 10 ** parameters.logrho}
        current_event.fit(Model, 'LM', flux_estimation_MCMC='MCMC')

        import pdb;
        pdb.set_trace()
        current_event.fits[0].produce_outputs()
        # print current_event.fits[0].fit_results
        plt.show()

    end = time.time()

    import pdb;
    pdb.set_trace()
    print end - start

    all_results = [('Fits.txt', results),
                   ('Fits_Error.txt', errors)]

    for file_name, values in all_results:
        np.savetxt(os.path.join(command_line.output_directory, file_name), np.array(values),
                   fmt="%s")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', default='PSPL')
    parser.add_argument('-i', '--input_directory',
                        default='/nethome/ebachelet/Desktop/Microlensing/OpenSourceProject/'
                                'SimulationML/OB160795/')
    parser.add_argument('-o', '--output_directory', default='/nethome/ebachelet/Desktop/Microlensing/'
                                                            'OpenSourceProject/Developement/Fitter/FSPL/')
    parser.add_argument('-c', '--claret',
                        default='/home/ebachelet/Desktop/nethome/Desktop/Microlensing/'
                                'OpenSourceProject/Claret2011/J_A+A_529_A75/')
    arguments = parser.parse_args()

    model = arguments.model

    main(arguments)
