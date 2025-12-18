<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import validTickers from '../assets/validTickers';

const ticker = ref('')
const forecastPeriod = ref(null)
const stockDetails = ref({})
const chosenModel = ref('LSTM')
const startDate = ref('2010-01-01')
const lookBack = ref(null)
const epochs = ref(null)
const batchSize = ref(null)
const modelOptions = ref(['LSTM'])
const maxDate = ref(new Date())

const emit = defineEmits(['request-model'])

const handleSubmit = (e) => {
    emit('request-model', e, ticker.value, forecastPeriod.value, chosenModel.value, startDate.value, lookBack.value, epochs.value, batchSize.value)
}

const handleChange = (e) => {
    axios.post("http://127.0.0.1:8000/stockDetail/" + e.input + "/")
    .then(response => {
        ticker.value = e.input;
        stockDetails.value = response.data;
    })
    .catch(e => console.log("Stock not available for forecasting."))
}

const updateMaxDate = (e) => {
    axios.post("http://127.0.0.1:8000/max-start-date/" + (e.value ?? 0) + "/")
    .then(res => {
        maxDate.value = new Date(res.data.max_start_date)
    })
}

</script>

<template>
    <h2 class="secondary-header">Stock Information</h2>
    <form>
        <label for="tickerSelector">Stock</label>
        <vue3-simple-typeahead
            id="tickerSelector"
            placeholder="Stock Ticker"
            :items="validTickers"
            @onBlur="handleChange"
            :minInputLength="1"
        />

        <StockDetail :ticker="ticker" :companyName="stockDetails.name" :price="stockDetails.price" :currency="stockDetails.currency"/>

        <label for="modelInput">Forecasting Model</label>
        <div>
            <SelectButton disabled="true" id="modelInput" v-model="chosenModel" :options="modelOptions"/>
        </div>
        <label for="dateInput">Data Start Date</label>
        <div>
            <DatePicker id="dateInput" :max-date="maxDate" v-model="startDate"/>
        </div>
        <label for="forecastInput">Forecast Length</label>
        <div>
            <InputNumber id="forecastInput" :min="1" v-model="forecastPeriod"/> 
        </div>
        <div v-if="chosenModel === 'LSTM'">
            <Divider/>
            <h4>LSTM Parameters</h4>
            <label for="lookBackLength">Look Back Length</label>
            <div>
                <InputNumber  id="lookbackLength" :min="1" :max="50" @input="updateMaxDate" v-model="lookBack"/>
            </div>
            <label for="epochsInput">Epochs</label>
            <div>
                <InputNumber id="epochsInput"  :min="1" :max="5" v-model="epochs"/>
            </div>
            <label for="batchSizeInput">Batch Size</label>
            <div>
                <InputNumber id="batchSizeInput"  :min="1" :max="30" v-model="batchSize"/>
            </div>
        </div>
        <PrimeButton class="forecast-button" label="Forecast" @click="handleSubmit"/>

    </form>
</template>

<style scoped>
.form-input {
    display: block;
}

.forecast-button {
    margin-top: 0.5rem;
}
</style>