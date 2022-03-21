# --------------------------------------------------------------------------
                    # Written by Aleksei Marianov, 2022
                    # marjanov.alexei@gmail.com
# --------------------------------------------------------------------------  

"""
The module is designed to read the VF-SWV data recorded on BioLogic potentiostats
and plot the respective 2D and 3D pictures.
"""

import pandas as pd
import glob as gb
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
from matplotlib.ticker import FormatStrFormatter



def extraction_of_swv(path: str, 
                    experimental_frequencies: np.ndarray,
                    array_of_frequencies_for_plotting: np.ndarray,
                    array_of_potentials_for_plotting: np.ndarray,
                    size_of_electrode: float,
                    dlc_correction: bool) -> np.ndarray:

    """
    Funciton extracts the VF-SWV response. Only data is produced and no plotting is happening at this stage!

    Parameters:
    path: str, folder with the .txt data files;
    experimental_frequencies: np.ndarray, a numpy array of the frequencies used in the experiment; 
    array_of_frequencies_for_plotting: np.ndarray, linearly spaced numpy array of the frequncies for plotting.
        The window defines the boundaries of plots and must be equal or less than those used to record the experimental
        data (Hz!);
    array_of_potentials_for_plotting: np.ndarray, linearly spaced numpy array covering the
        the window of interest (V vs NHE!);
    size_of_electrode: float, size of electrode;
    dlc_correction: bool, True applies correciton and False leaves the VF-SWV unchanged;

    Returns:
    2D np.ndarray containing freuency-normalized VF-SWV arrays;
    
    """

    files = sorted(gb.glob(path + "/*.txt"))
    js = []

    log_of_swv_frequency = np.log10(experimental_frequencies)
    for file, frequency in zip(files, experimental_frequencies):
        df = pd.read_table(file, index_col=None, header=0, delimiter="\t", encoding='ANSI')
        y1 = df["<I>/mA"]/size_of_electrode
        x1 = df['Ewe/V']+0.197
        j_f, j_b = [], []

        for i, j in enumerate(y1):
            if i % 2 == 0:
                j_f = np.append(j_f, j)
            else:
                j_b = np.append(j_b, j)
        dif_current = j_f - j_b
        # smoothening the noise
        dj = -dif_current*1000/frequency
        dj[dj < 0] = 0
        dj = savgol_filter(dj, 17, 3)

        e = np.linspace(max(x1), min(x1), len(dj))
        f = interp1d(e, dj, kind='cubic')
        j_new = f(array_of_potentials_for_plotting)

        # post-processing of the fitted curve
        j_new[j_new < 0] = 0

        if dlc_correction:
            cor = np.min(j_new)
            j_new = j_new - cor
        js.append(np.array(j_new))

    js = np.transpose(js)
    js1 = []
    for array in js:
        f1 = interp1d(log_of_swv_frequency, array, kind='cubic')
        new_a = f1(array_of_frequencies_for_plotting)
        js1.append(new_a)
    js = np.transpose(js1)
    return js



def plot_2D(x: np.ndarray, 
            y: np.ndarray, 
            z: np.ndarray,
            figure_name = None) -> None:

    """
    Funciton plots the VF-SWV response as a 2D map.

    Parameters:
    x: np.ndarray, linearly spaced 2D numpy array of potentials;
    y: np.ndarray, linearly spaced 2D numpy array of log(f) values;
    z: np.ndarray, VF-SWV response;
    figure_name: str, name of figure to export, if None, the figure will only be shown but not saved; 

    Returns:
    None;
    """

    font = {'family': 'serif', 'serif': 'Calibri', 'weight': 'bold', 'size': 12}
    plt.rc('font', **font)
    fig, ax = plt.subplots(1, 1, figsize=(6, 5))
    cont = ax.contourf(y, x, z, 100, cmap='jet')
    ax.set_xlabel('log[$f$(Hz)]', weight='bold')
    ax.set_ylabel('E, V vs NHE', weight='bold')
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    cbar = fig.colorbar(cont, ax=ax, format="%.0f")
    cbar.set_label('-\u2206 $j$/$f$, \u00B5C/cm\u00B2', weight='bold')
    plt.tight_layout()
    if figure_name != None:
        plt.savefig(f'{figure_name}.png', dpi=1200)
        plt.show()
    else:
        plt.show()


def plot_3D(x:np.ndarray, 
            y: np.ndarray, 
            z: np.ndarray,
            figure_name: str) -> None:

    """
    Funciton plots the VF-SWV response as a 3D map.

    Parameters:
    x: np.ndarray, linearly spaced 2D numpy array of potentials;
    y: np.ndarray, linearly spaced 2D numpy array of log(f) values;
    z: np.ndarray, VF-SWV response;
    figure_name: str, name of figure to export, if None, the figure will only be shown but not saved; 

    Returns:
    None;
    """

    fig = plt.figure(figsize=(6, 5))
    font = {'family': 'serif', 'serif': 'Calibri', 'weight': 'bold', 'size': 12}
    plt.rc('font', **font)

    ax = fig.add_subplot(111, projection='3d')

    ax.plot_surface(y, x, z, cmap='seismic', linewidth=0, rcount=50, ccount=50)
    ax.set_xlabel('log[ $f$(Hz) ]', weight='bold')
    ax.set_ylabel('E, V vs NHE', weight='bold')
    # ax.set_ylim(-0.6, -1.05)
    ax.set_zlabel('\u2206 $j$/$f$, \u00B5C/(cm\u00B2)', weight='bold')
    plt.tight_layout()
    if figure_name != None:
        plt.savefig(f'{figure_name}.png', dpi=1200)
        plt.show()
    else:
        plt.show()


# test
if __name__ == "__main__":

    # location of the SWV files:

    # Checking files for Alexander
    # path = r'C:\Documents\Collaborations\Undergraduate_student_projects\March_2022\Alexander_Russel\CoPc_VFSWV_txt_data'
    # path = r'C:\Documents\Collaborations\Undergraduate_student_projects\March_2022\Alexander_Russel\CoPc(OMe)8_VFSWV_txt_data'

    # Checking files for Inas
    # path = r'C:\Documents\Collaborations\Undergraduate_student_projects\March_2022\Inas_Ansari\CuO_with_CoPc'
    path = r'C:\Documents\Collaborations\Undergraduate_student_projects\March_2022\Inas_Ansari\CuO_pristine'

    # create arrays of step delay times (ms) and frequencies (Hz)
    step_times = np.array([0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8,
                        4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.4, 5.8, 6.2, 6.6, 7, 7.4, 7.8, 8.2, 8.6, 9, 9.4,
                9.8, 10.2, 10.6, 12.8, 13.6, 14.4, 15.2, 16, 17, 18, 19, 20, 22, 24, 26, 28, 34, 38, 42, 46, 50, 55,
                        60, 65, 70, 75, 80, 85, 90, 95, 100, 125, 150, 175, 200, 300, 400, 500, 750, 1000, 1500])
    frequencies = 500/step_times

    # define a window of interest across x and y axis
    e_boundary_highest, e_boundary_lowest = 0.8, -1.0
    log_frequency_highest, log_frequency_lowest = 3.09, -0.47

    # produce the linearly spaced arrays for interpolaiton and plotting
    e_new = np.linspace(e_boundary_highest, e_boundary_lowest, 100)
    freq_new = np.linspace(log_frequency_highest, log_frequency_lowest, 100)


    # generate the experimentally recorded 2D VF-SWV and make the linealry spaced 2D arrays for plotting
    x, y = np.meshgrid(e_new, freq_new)
    sq_w_v = extraction_of_swv(path=path,
                                experimental_frequencies=frequencies,
                                array_of_frequencies_for_plotting=freq_new,
                                array_of_potentials_for_plotting=e_new,
                                size_of_electrode=1.0, 
                                dlc_correction=False)
    
    # plot the experimental data
    plot_2D(x=x, 
            y=y, 
            z=sq_w_v, 
            figure_name=None)

    plot_3D(x=x, 
            y=y, 
            z=sq_w_v, 
            figure_name=None)

