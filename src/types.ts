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
    createdAt: string;
}

export type MarkerData = {
    id: number;
    latlng: number[];
    label: string | null;
}