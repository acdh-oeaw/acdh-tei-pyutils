# bin/bash

denormalize-indices -f "/home/daniel/Documents/Auden-Musulin/amp-app-dev/data/editions/*/*.xml" -i "/home/daniel/Documents/Auden-Musulin/amp-app-dev/data/indices/*.xml" -m './/tei:rs[@ref]/@ref' -t 'mentioned in ' -x './/tei:title[@level="a"]/text()'