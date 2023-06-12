export type GSIReverseGeocoderResponse = {
    results: {
        muniCd: string;
        lv01Nm: string;
    }
};

export type MarkerAPIData = {
    id: number;
    lat: number;
    lng: number;
    memo: string | null;
    createdAt: string;
}

export type MarkerData = {
    id: number;
    latlng: number[];
    memo: string | null;
    createdAt: string;
}

export type WindowGSIVarT = {
    MUNI_ARRAY: { [key: number]: string };
}