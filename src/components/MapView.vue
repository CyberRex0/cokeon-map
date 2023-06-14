<template>
    <div class="llmap">
        <l-map class="llmap" ref="map" v-model:zoom="zoom" :center="mapCenter" :use-global-leaflet="false" :options="{ contextmenu: true }" @update:center="updateCenterLatLng" @contextmenu="onMapContext">
            <l-control-layers :sortLayers="true" />
            <l-tile-layer
                v-for="provider in mapTileProvider"
                :url="provider.url"
                :layer-type="provider.type"
                :name="provider.name"
            ></l-tile-layer>
            <l-control v-if="isGPSSupported" class="leaflet-control control-tr" position="topright">
                <div class="lcontroltr">
                <el-button @click="getGeolocation">現在地取得</el-button>
                <br>
                <el-switch v-model="geoAutoUpdate" active-text="AUTO" inactive-text="MANUAL"></el-switch>
                <br>
                <el-button @click="moveLatLngDialogVisible = true">座標指定</el-button>
                <br>
                <el-button @click="addMarkerFromCenter">マーカー追加</el-button>
                </div>
            </l-control>
            <l-control class="leaflet-control" position="topleft">
                <b style="color: black">Powered by Leaflet<br/>made in Ukraine</b>
                <br>
                <b style="color: white; background-color: rgb(50,50,50);">
                    {{ currentLatLng[0] }}, {{ currentLatLng[1] }}<br>
                    {{ currentAddress }}<br>
                    <span v-if="geoAutoUpdate">{{ geoUpdateInfo.speed>0 ? Math.floor(geoUpdateInfo.speed) : '0' }}km/h &plusmn;{{ Math.floor(geoUpdateInfo.accuracy) }}m</span>
                </b>
            </l-control>
            <l-marker v-for="marker in markers" ref="markerRefs" :lat-lng="marker.latlng" :key="marker.id" @moveend="onMarkerDrag" @contextmenu="onMarkerContext" :icon="CokeOnIcon" :options="{id: marker.id, memo: marker.memo}">
                <l-tooltip>{{ marker.memo }}<br>追加日時: {{ marker.createdAt }}</l-tooltip>
            </l-marker>
            <l-marker :lat-lng="currentLatLng" :icon="MapCenterIcon"></l-marker>
            <l-circle v-if="mapContextMenuShow" :lat-lng="pointerLatLng" :radius="pointerCircleRadius" color="red" @contextmenu="()=> { return false; }" />

            <div v-show="markerContextMenuShow" ref="markerContextMenuRef" class="contextmenu markercontext">
                <el-button @click="removeMarkerClick">削除</el-button>
                <br>
                <el-button @click="editMarkerMemoClick">メモ編集</el-button>
                <br>
                <el-button @click="openGMapClick">Googleマップで見る</el-button>
            </div>
            <div v-show="mapContextMenuShow" ref="mapContextMenuRef" class="contextmenu mapcontext" oncontextmenu="return false;">
                <el-button @click="addMarkerCurrentClick">ここにマーカーを追加</el-button>
                <br>
                <el-button @click="openGMapCurrentClick">Googleマップで見る</el-button>
            </div>
        </l-map>
    </div>

    <el-dialog
        class="modal"
        v-model="moveLatLngDialogVisible"
        title="指定座標に移動"
        width="70vw"
    >
        <el-input style="width: 60%" v-model="customLat" placeholder="緯度 (例: 35.68114)" />
        <br>
        <el-input style="width: 60%" v-model="customLng" placeholder="経度 (例: 139.76703)" />

        <template #footer>
            <span class="dialog-footer">
                <el-button @click="moveLatLngDialogVisible = false">Cancel</el-button>
                <el-button type="primary" @click="moveToCustomLatLng">
                移動
                </el-button>
            </span>
        </template>
    </el-dialog>

    <el-dialog
        class="modal"
        v-model="editMarkerMemoDialogVisible"
        title="メモを編集"
        width="70vw"
    >

        <el-input
            v-model="markerMemo"
            :autosize="{ minRows: 4, maxRows: 6 }"
            type="textarea"
            placeholder=""
        />

        <template #footer>
            <span class="dialog-footer">
                <el-button @click="editMarkerMemoDialogVisible = false">Cancel</el-button>
                <el-button type="primary" @click="saveMarkerMemoClick">
                保存
                </el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import 'leaflet/dist/leaflet.css';
/*import 'element-plus/theme-chalk/dark/css-vars.css';*/
import { LMap, LTileLayer, LMarker, LTooltip, LControlLayers, LControl, LCircle } from "@vue-leaflet/vue-leaflet";
import { Ref, onMounted, onUnmounted, ref, watch } from 'vue';
import GSIAPI from '../gsi';
import { MapCenterIcon, CokeOnIcon } from '../icons';
import { MarkerAPIData, MarkerData } from '../types';
import { ElMessageBox, ElNotification, ElSwitch } from 'element-plus';

const mapTileProvider = [
    {
        url: 'https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}',
        type: 'base',
        name: '1 Google マップ',
    },
    {
        url: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        type: 'base',
        name: '2 Google マップ (衛星写真)',
    },
    {
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        type: 'base',
        name: '3 OpenStreetMap',
    },
];

const isGPSSupported = (navigator.geolocation !== undefined);
const map: any = ref(null);
const mapCenter: Ref<number[]> = ref([35.681148324168014, 139.76703858892955]);
const zoom: Ref<number> = ref(16);
const currentLatLng: Ref<number[]> = ref([0,0]);
const currentAddress: Ref<string> = ref('');
const customLat = ref('');
const customLng = ref('');
const markers: Ref<MarkerData[]> = ref([]);
const moveLatLngDialogVisible = ref(false);
const markerContextMenuShow = ref(false);
const markerContextMenuRef = ref();
let removeMarkerClick = null;
let editMarkerMemoClick = null;
const markerRefs = ref([]);
const markerMemo = ref('');
const editMarkerMemoDialogVisible = ref(false);
let saveMarkerMemoClick = null;
let openGMapClick = null;
const mapContextMenuShow = ref(false);
const mapContextMenuRef = ref();
let addMarkerCurrentClick = null;
const pointerLatLng = ref([0,0]);
const pointerCircleRadius = ref(50);
const geoAutoUpdate = ref(false);
let geoWatchHandle = null;
let openGMapCurrentClick = null;
const geoUpdateInfo: Ref<GeolocationCoordinates> = ref();

watch(zoom, () => {
    let z = 50 - (zoom.value * 2.5);
    if (z < 0) z = 0;
    pointerCircleRadius.value = z;
});

watch(geoAutoUpdate, () => {
    if (geoAutoUpdate.value === true) {
        if (!geoWatchHandle) {
            geoWatchHandle = navigator.geolocation.watchPosition(async (p) => {
                mapCenter.value = [p.coords.latitude, p.coords.longitude];
                geoUpdateInfo.value = p.coords;
                await updateCenterLatLng({lat: p.coords.latitude, lng: p.coords.longitude});
            }, () => {}, { enableHighAccuracy: true });
        }
    } else {
        if (geoWatchHandle) {
            navigator.geolocation.clearWatch(geoWatchHandle);
            geoWatchHandle = null;
        }
    }
});

function onMarkerDrag(ev: { target: any; }): void {
    console.log(ev.target);
}

async function onMapContext(ev) {
    const target = ev.target;
	console.log(map.value.leafletObject);
    if (target.classList.contains('llmap')) {
        ev.preventDefault();
        mapContextMenuRef.value.style.top = ev.pageY + 'px';
        mapContextMenuRef.value.style.left = ev.pageX + 'px';
        const platlng = map.value.leafletObject.mouseEventToLatLng(ev);
        pointerLatLng.value =[platlng.lat, platlng.lng];
        addMarkerCurrentClick = async () => {
            mapContextMenuShow.value = false;
            await addMarker(platlng.lat, platlng.lng);
        };
        openGMapCurrentClick = () => {
            mapContextMenuShow.value = false;
            openGMap(platlng.lat, platlng.lng);
        }
        mapContextMenuShow.value = true;
        document.addEventListener('click', checkClickOutOfMapMenu);
    }
}

async function onMarkerContext(ev: { target: any; }) {
    const target = ev.target;
    const iconRect = target.dragging._marker._icon.getBoundingClientRect();
    markerContextMenuRef.value.style.top = iconRect.top + 'px';
    markerContextMenuRef.value.style.left = iconRect.left + 'px';
    markerContextMenuShow.value = true;
    document.addEventListener('click', checkClickOutOfCtxMenu);
    removeMarkerClick = () => {
        removeMarker(target.options.id);
    };
    editMarkerMemoClick = () => {
        markerContextMenuShow.value = false;
        markerMemo.value = target.options.memo;
        saveMarkerMemoClick = async () => {
            await saveMarkerMemo(target.options.id, markerMemo.value);
        };
        editMarkerMemoDialogVisible.value = true;
    }
    openGMapClick = () => {
        openGMap(target._latlng.lat, target._latlng.lng);
    };
    return;
}

function checkClickOutOfCtxMenu(e) {
    if (!e.target.closest('.markercontext')) {
        markerContextMenuShow.value = false;
        document.removeEventListener('click', checkClickOutOfCtxMenu);
    }
}

function checkClickOutOfMapMenu(e) {
    if (!e.target.closest('.mapcontext')) {
        mapContextMenuShow.value = false;
        document.removeEventListener('click', checkClickOutOfMapMenu);
    }
}

async function removeMarker(mid) {
    markerContextMenuShow.value = false;
    ElMessageBox.confirm('削除しますか？').then(async () => {
        const f = await fetch('/api/v1/markers/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: mid }),
        });
        if (f.ok) {
            markers.value = markers.value.filter(v => v.id !== mid);
            ElNotification({
                title: 'マーカーを削除しました',
                type: 'success',
            });
        } else {
            ElNotification({
                title: 'マーカーを削除できませんでした',
                type: 'error',
            });
        }
    }).catch(() => {});
}

async function saveMarkerMemo(mid, memo) {
    const f = await fetch('/api/v1/markers/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: mid, memo: memo }),
    });
    if (f.ok) {
        for (let index=0; index < markers.value.length; index++) {
            if (markers.value[index].id == mid) {
                markers.value[index].memo = memo;
                break;
            }
        }
        editMarkerMemoDialogVisible.value = false;
        ElNotification({
                title: 'メモを更新しました',
                type: 'success',
        });
    } else {
        ElNotification({
                title: 'メモを更新できませんでした',
                type: 'error',
        });
    }
}

function openGMap(lat, lng) {
    window.open(`https://www.google.com/maps/search/?api=1&query=${lat},${lng}`);
}

function getGeolocation(): void {
    if (navigator.geolocation) {
        const notify = ElNotification({
                title: '位置情報を取得しています…',
                message: '数秒かかります',
                duration: 0
        });
        navigator.geolocation.getCurrentPosition((g) => {
            mapCenter.value = [g.coords.latitude, g.coords.longitude];
            currentLatLng.value = [g.coords.latitude, g.coords.longitude];
            notify.close();
        }, () => {}, {
            enableHighAccuracy: true,
        });
    } else {
        ElNotification({
                title: '位置情報を取得できません',
                message: 'ブラウザがサポートしていません。',
                type: 'warning',
        });
    }
}

async function updateCenterLatLng(center: {lat: number, lng: number}) {
    currentLatLng.value = [center.lat, center.lng];
    const addr: string = await GSIAPI.fetchMapAddressByLatLng(center.lat, center.lng);
    currentAddress.value = addr;
}

async function addMarkerFromCenter() {
    await addMarker(currentLatLng.value[0], currentLatLng.value[1]);
}

async function addMarker(lat, lng) {
    const f = await fetch('/api/v1/markers/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ lat: lat, lng: lng }),
    });
    if (f.ok) {
        const res: MarkerAPIData = await f.json();
        console.log(res);
        const v = {
            id: res.id,
            latlng: [Number(res.lat), Number(res.lng)],
            memo: res.memo,
            createdAt: res.createdAt,
        };
        markers.value.push(v);
        ElNotification({
                title: 'マーカーを追加しました',
                type: 'success',
        });
    } else {
        ElNotification({
                title: 'マーカーを追加できませんでした',
                type: 'error',
        });
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
                id: m.id,
                memo: m.memo,
                createdAt: m.createdAt,
            });
        }
        markers.value = converted;
    } else {
        alert('error!');
    }
}

function moveToCustomLatLng() {
    moveLatLngDialogVisible.value = false;
    mapCenter.value = [Number(customLat.value), Number(customLng.value)];
}

onMounted(async () => {
    getGeolocation();
    getMarkerList();

    /*const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const darkModeOn = darkModeMediaQuery.matches;
    if (darkModeOn) {
        document.documentElement.classList.add('dark');
    }

    darkModeMediaQuery.addEventListener('change', (e) => {
        const darkModeOn = e.matches;
        if (darkModeOn) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    });*/
});

onUnmounted(() => {
    if (geoWatchHandle) {
        navigator.geolocation.clearWatch(geoWatchHandle);
        geoWatchHandle = null;
    }
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

.lcontroltr button {
    margin-top: 8px;
}

.control-tr {
    padding: 2px;
    background-color: rgba(255,255,255,0.8);
    border-radius: 4px;
}

.control-tr button {
    width: 100%;
}

.contextmenu {
    position: absolute;
    padding: 4px;
    /*width: 200px;
    height: 300px;*/
    background-color: rgba(255, 255, 255, 0.7);
    /*border: 2px solid black;*/
    z-index: 99999;
    border-radius: 2px;
}

.contextmenu button {
    width: 100%;
}
</style>