#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

def dB_from_gain(gain):
	"""Converts gain into decibals."""
	dB = 20 * np.log10(gain)
	return dB

def gain_from_dB(dB):
	"""Converts decibals to gain."""
	dB = 10**(dB/20)
	return dB

def open_loop_gain(s, freq_crossover):
	"""Open loop gain in V/V."""
	freq_open_loop_gain = (2 * np.pi * freq_crossover) / s  # gain, for any VFB opamp
	open_loop_gain_magnitude = np.abs(freq_open_loop_gain)
	return open_loop_gain_magnitude

def closed_loop_3dB(R_f, R_g, freq_crossover):
	"""Closed loop gain, for both non/inverting VFB config."""
	freq_closed_loop_gain = freq_crossover * (R_g / (R_f * R_g))  # gain, V/V
	closed_loop_gain_magnitude = np.abs(freq_closed_loop_gain)
	return closed_loop_gain_magnitude

def vout_vin_closed_loop_inverting_gain(R_f, R_g, freq_crossover, s):
	"""Vout / Vin inverting config closed loop gain."""
	inverting_closed_loop_gain = (-2 * np.pi * freq_crossover * R_f) / (s * (R_f + R_g) + 2 * np.pi * freq_crossover * R_g)
	inverting_closed_loop_gain_magnitude = np.abs(inverting_closed_loop_gain)
	return inverting_closed_loop_gain_magnitude

def vout_vin_closed_loop_noninverting_gain(R_f, R_g, freq_crossover, s):
    noninverting_closed_loop_gain = (2 * np.pi * freq_crossover * (R_g + R_f)) / (((R_f + R_g) * s) + 2 * np.pi * freq_crossover * R_g)
    noninverting_closed_loop_gain_magnitude = np.abs(noninverting_closed_loop_gain)
    return noninverting_closed_loop_gain_magnitude

def beta(r_f, c_f, c_in, s):
	"""what"""
	beta = (1 + (r_f * c_f * s)) / (1 + (r_f * (c_in + c_f) * s))
	beta_magnitude = np.abs(beta)
	return beta_magnitude

def transimpedance_amp_output(current, r_f, open_loop_gain, beta):
	"""Maybe.  Open loop gain is an array based on frequency."""
	vout = current * (- r_f / (1 + (1/(open_loop_gain * beta))))
	vout_magnitude = np.abs(vout) # as actual output would be negative
	return vout_magnitude

def zeroth_pole_freq(feedback_gain, total_cap, feedback_cap):
	"""Zeroth pole frequency (Hz) based on capacitance and feedback gain"""
	freq_zero_pole = 1 / (2 * np.pi * feedback_gain * (total_cap + feedback_cap)) # Hz
	return freq_zero_pole

def first_pole_freq(feedback_resistor, feedback_cap):
	"""First pole frequency (Hz) based on feedback resistor and cap."""
	freq_first_pole = 1 / (2 * np.pi * feedback_resistor * feedback_cap)  # Hz
	return freq_first_pole


if __name__== "__main__":
	import argparse
	my_parser = argparse.ArgumentParser(prog='general_photodiode_signal_chain', description='Photodiode Transimpedance Amplifier Calcs')
	my_parser.add_argument('tia_gain_bandwidth_product', metavar='tia_gain_bandwidth_product', type=float, nargs='?', default=200e6,  help='TIA opamp GBWP (200e6 Hz)') # temp Hz, OPA659
	my_parser.add_argument('tia_gain_resistor', metavar='tia_gain_resistor', type=float, nargs='?', default=1e3, help='TIA gain set resistor (1 kOhms)')  # temp, R_f
	my_parser.add_argument('tia_internal_cap', metavar='tia_internal_cap', type=float, nargs='?', default=3.5e-12, help='Total input capacitance of TIA (3.5 pF)')  # temp, OPA659
	my_parser.add_argument('pd_capacitance', metavar='pd_capacitance', type=float, nargs='?', default=15e-12, help='Photodiode capacitance at bias voltage (15 pF)')  # F, temp
	my_parser.add_argument('goal_freq', metavar='goal_freq', type=float, nargs='?', default=100e3, help='Maximum user frequency (10 kHz)')  # Hz, temp)
	args = my_parser.parse_args()

	tia_gain_bandwidth_product = args.tia_gain_bandwidth_product
	tia_gain_resistor = args.tia_gain_resistor
	tia_internal_cap = args.tia_internal_cap
	pd_capacitance = args.pd_capacitance
	goal_freq = args.goal_freq
	total_cap = pd_capacitance +  tia_internal_cap # temp
	feedback_cap = 1/ (2 * np.pi *  tia_gain_resistor * goal_freq)
	# feedback_cap = np.sqrt(total_cap / (2 * np.pi * tia_gain_resistor * tia_gain_bandwidth_product))

	freq_range = np.arange(0.1, 10e6) # Hz
	w = 2 * np.pi * freq_range
	s = w * 1j
	R_g = 1  # Ohms, In this case for transimpedance amplifier this value is the pcb trace resistance from PD to opamp
	tia_open_loop_gain = open_loop_gain(s, tia_gain_bandwidth_product)
	tia_closed_loop_3dB = closed_loop_3dB(tia_gain_resistor, R_g, tia_gain_bandwidth_product)
	tia_vout_vin_closed_loop_inverting = vout_vin_closed_loop_inverting_gain(tia_gain_resistor, R_g, tia_gain_bandwidth_product, s)

	# Testing
	current = 64e-6  # I think
	opamp_beta = beta(tia_gain_resistor, feedback_cap, total_cap, s) # Correct
	tia_volt_output = transimpedance_amp_output(current, tia_gain_resistor, tia_open_loop_gain, opamp_beta) # Correct

	z_one = zeroth_pole_freq(tia_gain_resistor, total_cap, feedback_cap) # Correct
	p_one = first_pole_freq(tia_gain_resistor, feedback_cap) # Correct
	# f_zero = np.sqrt(z_one * tia_gain_bandwidth_product)
	# f_c = tia_gain_bandwidth_product / (1 + (total_cap/feedback_cap))

	print(f"TIA closed loop frequency 3dB point: {tia_closed_loop_3dB} Hz") # Hz with GBW opamp and R_f
	print(f"Z1: {z_one} Hz")
	print(f"P1: {p_one} Hz")
	# print(f"F0: {f_zero} Hz")
	# print(f"Fc: {f_c} Hz")

	# Plots, gain
	fig, ax = plt.subplots(2) # ncols=1, nrows=1
	ax[0].loglog(freq_range, tia_open_loop_gain, color='red', label='Open loop',)  # Correct
	ax[0].loglog(freq_range, tia_vout_vin_closed_loop_inverting, color='green', label='Closed loop')  # Think correct
	# ax[0].loglog(freq_range, (1 / opamp_beta), color='blue', label='1/Beta')  # Correct
	# ax.loglog(freq_range, (1 / (opamp_beta) * tia_gain_resistor), color='blue', label='Noise gain') # Think correct
	# ax.plot(freq_range, (tia_volt_output / current), color='green', label='I-to-V gain') # Correct
	
	ax[0].loglog(z_one,tia_gain_resistor, marker="o", label='Z1')
	ax[0].loglog(p_one,tia_gain_resistor, marker="o", label='P1')
	# ax.loglog(f_zero,tia_gain_resistor, marker="o", label='F0')
	ax[0].loglog(tia_closed_loop_3dB,tia_gain_resistor, marker="o", label='Fc')
	ax[0].legend(loc="upper right")
	ax[0].set_title('Bode Plot')
	ax[0].set_xlabel('Frequency [Hz]')
	ax[0].set_ylabel('Gain [V/V]')
	ax[0].grid(True, which='both', axis='both')
	# ax[0].set_yscale('symlog')
	# ax[0].set_xscale('symlog')
	# fig.savefig("figure3.pdf")
	# fig.show()

	# Next change gain to dB scale and plot
	ax[1].loglog(freq_range, dB_from_gain(tia_open_loop_gain), color='red', label='Open loop',)  # Correct
	ax[1].loglog(freq_range, dB_from_gain((1 / opamp_beta)), color='blue', label='1/Beta')  # Correct
	ax[1].set_xlabel('Frequency [Hz]')
	ax[1].set_ylabel('Gain [dB]')
	ax[1].grid(True, which='both', axis='both')
	fig.savefig("figure4.pdf")
	fig.show()