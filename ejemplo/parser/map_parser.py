def parser(self, file_path: str) -> None:
    try:
        # with open("file_datos.txt","r") as archivo:
        with open(file_path, "r") as data_file:
            for l in data_file:
                linea = l.strip()
                if not linea: continue
                
                key, _, rest = l.partition(":")
                value_gross, _, optionals_raw = rest.partition("[")

                value = value_gross.strip()

                color = None
                zone = "normal"
                max_dorne = 1

                if optionals_raw:
                    bloque_opts = optionals_raw.replace("]", "").split()
                    for item in bloque_opts:
                        if "=" in item:
                            opt_k, opt_v = item.split("=")
                            
                            if opt_k == "color":
                                color = opt_v
                            elif opt_k == "zone":
                                zone = opt_v
                            elif opt_k == "max_drone":
                                max_drone = int(optv)
        # instanciar clase (key, value, color, zone, max_drone)    
        print(f"Instanciando: {key} | Val: {value} | Color: {color} | Zone: {zone} | MAx: {max_drone}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return
    # finally:
        # file.close()

class Zona:
    def __init__(self, nombre, limite_x, limite_y, es_restringida=False):
        self.nombre = nombre
        self.limite_x = limite_x
        self.limite_y = limite_y
        self.es_restringida = es_restringida

class Mapa:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.zonas = []
        self.partida = (0, 0)
        self.llegada = (ancho, alto)

    def puede_moverse(self, x, y):
        # Aquí verificas si (x, y) toca alguna zona restringida
        for zona in self.zonas:
            if zona.contiene_punto(x, y) and zona.es_restringida:
                return False
        return True