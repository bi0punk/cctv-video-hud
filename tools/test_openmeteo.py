#!/usr/bin/env python3
import argparse
import json
from telemetry import fetch_openmeteo


def main():
    parser = argparse.ArgumentParser(description="Prueba Open-Meteo por coordenadas.")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    args = parser.parse_args()
    data = fetch_openmeteo(args.lat, args.lon)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
