import numpy as np
import pandas as pd

# Constants
m_e = 0.511e-3  # Mass of electron in GeV (0.511 MeV/c^2)


def calculate_Q2(E, Theta):
    """
    Calculate the four-momentum transfer squared (Q^2) from energy (E) and scattering angle (Theta).
    Theta is in degrees.
    """

    Theta_rad = np.radians(Theta)  # Convert Theta from degrees to radians
    return 2 * E**2 * (1 - np.cos(Theta_rad))


def EnergyLossFromX(data: pd.DataFrame) -> None:
    """
    the fifth column of any E02-019 (Fomin:2010ei) data was in x=Q^2/2mν instead of energy loss,
    this function recalculates it
    """
    # Iterate over the rows of the DataFrame
    for index, row in data.iterrows():
        # Check if the citation matches 'Fomin:2010ei'
        if row["citation"] == "Fomin:2010ei":
            E = row["E (GeV)"]  # Energy (GeV)
            Theta = row["Theta (degrees)"]  # Scattering angle (degrees)
            x = row["energy loss (GeV)"]  # x (Energy loss or variable)

            try:
                Theta = float(Theta)
                E = float(E)
                x = float(x)
            except (ValueError, TypeError):
                print("Warning: Invalid  encountered. Skipping.")
                return np.nan

            # Calculate Q^2
            Q2 = calculate_Q2(E, Theta)

            # Calculate energy loss (GeV) from x using the formula: energy loss = Q^2 / (2 * m * x)
            if x != 0:  # Avoid division by zero
                energy_loss = Q2 / (2 * m_e * x)
            else:
                energy_loss = np.nan  # If x is zero, set energy loss to NaN

            print(f"Q2 = {Q2}, x = {x}, energy_loss = {energy_loss}")

            # Update the 'energy loss (GeV)' column in place
            data.at[index, "energy loss (GeV)"] = energy_loss / 1000.0
