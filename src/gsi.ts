import { GSIReverseGeocoderResponse, WindowGSIVarT } from "./types";

const GSI: WindowGSIVarT = window.GSI;

export default {
    GSI_API_BASE: 'https://mreversegeocoder.gsi.go.jp',
    async fetchMapAddressByLatLng(lat: number, lng: number): Promise<string> {
        const f = await fetch(`${this.GSI_API_BASE}/reverse-geocoder/LonLatToAddress?lat=${lat}&lon=${lng}`);
        if (f.ok) {
            const res: GSIReverseGeocoderResponse = await f.json();
            if (res) {
                if (Object.keys(res).length !== 0) {
                    const muniCd = Number(res.results.muniCd);
                    if (GSI.MUNI_ARRAY[muniCd]) {
                        const muniA = GSI.MUNI_ARRAY[muniCd].split(',');
                        let addr = '';
                        for (let i=1; i<muniA.length; i+=2) {
                            addr += muniA[i];
                        }
                        return addr + res.results.lv01Nm;
                    }
                }
            }
        }
        return '';
    }
}