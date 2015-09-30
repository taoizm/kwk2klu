#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
import tables as tb


def main():
    argv = sys.argv
    argc = len(argv)

    if argc == 1:
        path = os.getcwd()
        basename = os.path.basename(path)
    elif argc == 2:
        basename = argv[1]
    else:
        print ('Usage: python %s basename\n') % argv[0]
        print ('Execute in the directory where contains .kwik and .kwx file.'
               'If dirname and basename are the same, you don\'t need to'
               'specify basename as an argument.')
        sys.exit()

    try:
        kwik = tb.open_file(basename+'.kwik', 'r')
        kwx = tb.open_file(basename+'.kwx', 'r')
    except IOError:
        print 'Error: Files do not exist or cannot be opened.'
        sys.exit()

    shlist = kwik.root.channel_groups.__members__
    shlist = sorted(shlist)
    nshanks = len(shlist)

    for i in shlist:
        print 'processing shank %s/%s' % (i, nshanks)

        clu = kwik.root.channel_groups.__getattr__(i).spikes.clusters.main[:]
        res = kwik.root.channel_groups.__getattr__(i).spikes.time_samples[:]
        fet = kwx.root.channel_groups.__getattr__(i).features_masks[:, :, 0]
        spk = kwx.root.channel_groups.__getattr__(i).waveforms_filtered[:, :, :]

        factor = 2.**12/np.abs(fet).max()
        fet = (fet * factor).astype('int16')
        fet = np.hstack((fet[:, :], res[:, np.newaxis]))

        nclu = np.max(clu)
        nfet = fet.shape[1]
        nspk = spk.shape[0]

        print 'number of clusters: %d' % nclu
        print 'number of spikes: %d' % nspk

        np.savetxt('./'+basename+'.clu.'+i, clu, fmt='%i',
                   header='%d' % nclu, comments='')
        np.savetxt('./'+basename+'.res.'+i, res, fmt='%i')
        np.savetxt('./'+basename+'.fet.'+i, fet, fmt='%i',
                   header='%d' % nfet, comments='')
        with open('./'+basename+'.spk.'+i, 'wb') as f:
            f.write(spk)

    kwik.close()
    kwx.close()


if __name__ == "__main__":
    main()
