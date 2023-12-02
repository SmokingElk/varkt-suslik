from orbit_entering_model import calculateOrbitData
from plotter import makeFieldPlot

FUEL_MASS_MIN = 0.001
FUEL_MASS_MAX = 0.02

PAYLOAD_MASS_MIN = 0.001
PAYLOAD_MASS_MAX = 0.01

STEPS_COUNT = 80


def lerp(a, b, c):
    return a + (b - a) * c


def main():
    orbitReachableField = []

    for j in range(0, STEPS_COUNT):
        row = []

        for i in range(0, STEPS_COUNT):
            fuelMass = lerp(FUEL_MASS_MIN, FUEL_MASS_MAX, i / (STEPS_COUNT - 1))
            payloadMass = lerp(PAYLOAD_MASS_MIN, PAYLOAD_MASS_MAX, j / (STEPS_COUNT - 1))

            tr, ap, ad, pp, pd, crash, orbitWasReached = calculateOrbitData(fuelMass, payloadMass)
            
            if orbitWasReached:
                row.append(0)
            else:
                row.append(2 if crash else 1)

        orbitReachableField.append(row)
        print(f"Progress {int((j + 1) / STEPS_COUNT * 100)}%")

    print("Calculations were completed")

    makeFieldPlot(
        orbitReachableField,
        FUEL_MASS_MIN,
        FUEL_MASS_MAX,
        PAYLOAD_MASS_MIN,
        PAYLOAD_MASS_MAX, 
        "./model_1/mass_fuel_plot.png"
    )


if __name__ == "__main__":
    main()