<template>
    <div class="llmap">
        <l-map class="llmap" ref="map" v-model:zoom="zoom" :center="mapCenter" :use-global-leaflet="false" @update:center="updateCenterLatLng">
            <l-control-layers />
            <l-tile-layer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                layer-type="base"
                name="OpenStreetMap"
            ></l-tile-layer>
            <l-control v-if="isGPSSupported" class="leaflet-control leaflet-demo-control" position="topright">
                <button @click="getGeolocation">現在地取得</button>
                <br>
                <button @click="addMarker">マーカー追加</button>
            </l-control>
            <l-control class="leaflet-control" position="topleft">
                <b style="color: black">Powered by Leaflet<br/>made in Ukraine</b>
                <br>
                <b style="color: white; background-color: rgb(50,50,50);">
                    {{ currentLatLng[0] }}, {{ currentLatLng[1] }}<br>
                    {{ currentAddress }}
                </b>
            </l-control>
            <l-marker v-for="marker in markers" :lat-lng="marker.latlng" :key="marker.id" @moveend="onMarkerDrag" @contextmenu="onMarkerContext" :icon="CokeOnIcon" :options="{id: marker.id}">
                <l-tooltip>{{ marker.label }}</l-tooltip>
            </l-marker>
            <l-marker :lat-lng="currentLatLng" :icon="MapCenterIcon"></l-marker>
        </l-map>
    </div>
</template>

<script setup lang="ts">
import 'leaflet/dist/leaflet.css';
import { LMap, LTileLayer, LMarker, LTooltip, LControlLayers, LControl } from "@vue-leaflet/vue-leaflet";
import { Ref, onMounted, ref } from 'vue';
import GSI from '../gsi';
import { MapCenterIcon, CokeOnIcon } from '../icons';
import { MarkerAPIData, MarkerData } from '../types';
import { marker } from 'leaflet';

const isGPSSupported = (navigator.geolocation !== undefined);
const map: any = ref(null);
const mapCenter: Ref<number[]> = ref([35.681148324168014, 139.76703858892955]);
const zoom: Ref<number> = ref(16);
const currentLatLng: Ref<number[]> = ref([0,0]);
const currentAddress: Ref<string> = ref('');

const markers: Ref<MarkerData[]> = ref([]);


function onMarkerDrag(ev: { target: any; }): void {
    console.log(ev.target);
}

async function onMarkerContext(ev: { target: any; }) {
    const target = ev.target;
    if (window.confirm(`${target.options.id} を削除しますか？`)) {
        const f = await fetch('/api/v1/markers/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: target.options.id }),
        });
        if (f.ok) {
            markers.value = markers.value.filter(v => v.id !== target.options.id);
        } else {
            alert('error!');
        }
    }
}

function getGeolocation(): void {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((g) => {
            mapCenter.value = [g.coords.latitude, g.coords.longitude];
            currentLatLng.value = [g.coords.latitude, g.coords.longitude];
        });
    }
}

async function updateCenterLatLng(center: {lat: number, lng: number}) {
    currentLatLng.value = [center.lat, center.lng];
    const addr: string = await GSI.fetchMapAddressByLatLng(center.lat, center.lng);
    currentAddress.value = addr;
}

async function addMarker() {
    const f = await fetch('/api/v1/markers/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ lat: currentLatLng.value[0], lng: currentLatLng.value[1] }),
    });
    if (f.ok) {
        const res: MarkerData = await f.json();
        markers.value.push({
            id: res.id,
            latlng: res.latlng,
            label: res.label,
        });
    } else {
        alert('error!');
    }
}

async function getMarkerList() {
    const f = await fetch('/api/v1/markers/list');
    if (f.ok) {
        const l: MarkerAPIData[] = await f.json();
        const converted = [];
        for (const m of l) {
            converted.push({
                latlng: [m.lat, m.lng],
                label: m.createdAt,
                id: m.id,
            });
        }
        markers.value = converted;
    } else {
        alert('error!');
    }
}

onMounted(async () => {
    getGeolocation();
    getMarkerList();
});

</script>

<style scoped>
.llmap {
    width: 100%;
    height: 100%;
}

.cross { /* 十字アイコン */
	color: black;
	background: transparent;
	width: 36px; height: 36px;
}
.cross::before {
	content: "";
	position: absolute;
	top: -13px; left: 3px;
	width: 2px; height: 7px;
	border-top: 13px solid black;
	border-bottom: 13px solid black;
	border-radius: 2px;
}
.cross::after {
	content: "";
	position: absolute;
	top: 3px; left: -14px;
	width: 7px; height: 2px;
	border-left: 13px solid black;
	border-right: 13px solid black;
	border-radius: 2px;
}
</style>