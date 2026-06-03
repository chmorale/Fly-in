import sys
from parser.map_parser import Parser
from simulator.simulator import Simulator

def main() -> None:
    if len(sys.argv)<2:
        print("error: Se debe indicar ruta del mapa")
        print("Uso: python3 main.py <ruta_del_mapa>")
        return
    
    map_path: str = sys.argv[1]

    try:
        parser = Parser()
        map = parser.parse(map_path)

        sim = Simulator(map)
        sim.run()
    except Exception as e:
        print(f"Error al procesar el mapa: {e}")

if __name__ == "__main__":
    main()