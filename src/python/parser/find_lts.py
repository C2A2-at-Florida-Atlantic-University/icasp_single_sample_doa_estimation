"""
 find_lts.py

 Library for generating different training sequences

---------------------------------------------------------------------
 Copyright © 2018-2019. Rice University.
 RENEW OPEN SOURCE LICENSE: http://renew-wireless.org/license
---------------------------------------------------------------------
"""

import numpy as np
import generate_sequence as gen_seq
def find_lts(iq, thresh=0.8, us=1, cp=32, flip=False, lts_seq=[]):
	"""
		Find the indices of LTSs in the input "iq" signal (upsampled by a factor of "up").
		"thresh" sets sensitivity.
		Inputs:
			iq: IQ samples
			thresh: threshold to detect peak
			us: upsampling factor, needed for generate_training_seq() function
			cp: cyclic prefix
			flip: Flag to specify order or LTS sequence.
			lts_seq: if transmitted lts sequence is provided, use it, otherwise generate it
		Returns:
			best_pk: highest LTS peak,
			lts_pks: the list of all detected LTSs, and
			lts_corr: the correlated signal, multiplied by itself delayed by 1/2 an LTS
	"""
	debug = False

	np.seterr(divide='ignore', invalid='ignore')

	lts_seq = np.asarray(lts_seq)
	if lts_seq.size == 0:
		lts, lts_f = gen_seq.generate_training_seq(preamble_type='lts', cp=cp, upsample=us)
		peak_spacing = 64
	else:
		lts = lts_seq
		peak_spacing = 80

	lts_tmp = lts[-64:]
	if flip:
		lts_flip = lts_tmp[::-1]
	else:
		lts_flip = lts_tmp

	lts_flip_conj = np.conjugate(lts_flip)
	sign_fct = iq/abs(iq) # Equivalent to Matlab's sign function (X/abs(X))
	sign_fct = np.nan_to_num(sign_fct) # Replace NaN values
	lts_corr = np.abs(np.convolve(lts_flip_conj, sign_fct))

	lts_pks = np.where(lts_corr > (thresh * np.max(lts_corr)))
	lts_pks = np.squeeze(lts_pks)
	x_vec, y_vec = np.meshgrid(lts_pks, lts_pks)

	second_peak_idx, y = np.where((y_vec - x_vec) == peak_spacing)

	if not second_peak_idx.any():
		if debug:
			print("NO LTS FOUND!")
		best_pk = []
	else:
		best_pk = lts_pks[second_peak_idx[0]]

	if debug:
		if lts_pks.size > 1:
			fig = plt.figure()
			ax1 = fig.add_subplot(2, 1, 1)
			ax1.grid(True)
			ax1.plot(np.abs(iq))
			ax2 = fig.add_subplot(2, 1, 2)
			ax2.grid(True)
			ax2.stem(np.abs(lts_corr))
			ax2.scatter(lts_pks, 2 * np.ones(len(lts_pks)))
			plt.show()

	return best_pk, lts_pks, lts_corr