"""
This module contains necessary caoculations to recalculate x to energy loss for Fomin:2010ei data
"""

import numpy as np
import pandas as pd

# Constants
M_E = 0.511e-3  # Mass of electron in GeV (0.511 MeV/c^2)


def calculateQ2(energy: float, theta: float) -> float:
    """
    Calculate the four-momentum transfer squared (Q^2) from energy (E) and scattering angle (Theta).
    Args:
    energy (float): electron energy in GeV
    theta (float): scattering angle in degrees
    """

    theta_rad = np.radians(theta)  # Convert Theta from degrees to radians
    return 2 * energy**2 * (1 - np.cos(theta_rad))


def energy_loss_from_x(data: pd.DataFrame) -> None:
    """
    the fifth column of any E02-019 (Fomin:2010ei) data was in x=Q^2/2mν instead of energy loss,
    this function recalculates it and modifies data inplace
    Args:
    data (pd.DataFrame): dataset where x needs to be recalculated to the energy loss
    """
    # Iterate over the rows of the DataFrame
    for index, row in data.iterrows():
        # Check if the citation matches 'Fomin:2010ei'
        if row["citation"] == "Fomin:2010ei":
            energy = row["E (GeV)"]  # Energy (GeV)
            theta = row["Theta (degrees)"]  # Scattering angle (degrees)
            x = row["energy loss (GeV)"]  # x (Energy loss or variable)

            try:
                theta = float(theta)
                energy = float(energy)
                x = float(x)
            except (ValueError, TypeError):
                print("Warning: Invalid  encountered. Skipping.")
                continue

            # Calculate Q^2
            Q2 = calculateQ2(energy, theta)

            # Calculate energy loss (GeV) from x using the formula: energy loss = Q^2 / (2 * m * x)
            if x != 0:  # Avoid division by zero
                energy_loss = Q2 / (2 * M_E * x)
            else:
                energy_loss = np.nan  # If x is zero, set energy loss to NaN

            # print(f"Q2 = {Q2}, x = {x}, energy_loss = {energy_loss}")

            # Update the 'energy loss (GeV)' column in place
            data.at[index, "energy loss (GeV)"] = energy_loss / 1000.0
