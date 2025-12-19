<script setup>
import axios from 'axios';
import { ref } from 'vue';
import LSTMDetails from './components/LSTMDetails.vue';
import { useToast } from 'primevue/usetoast'
import Toast from 'primevue/toast';

const modelParameters = ref('')
const modelDetails = ref('')
const modelPrices = ref('');
const modelAccuracy = ref('')
const modelExists = ref(false);
const loadingModel = ref(false)
const toast = useToast();

// Requests to forecast financial data
const handleRequestModel = (e, inputTicker, inputForecastPeriod, chosenModel, startDate, lookBack, epochs, batchSize) => {
  loadingModel.value = true

  axios.post("http://127.0.0.1:8000/lstmForecast/", {
    ticker: inputTicker,
    forecastLength: inputForecastPeriod,
    sampleStartDate: startDate.toISOString().substring(0,10),
    lookBack: lookBack,
    epochs: epochs,
    batchSize: batchSize
  })
  .then(response => {
    modelParameters.value = response.data.parameters,
    modelDetails.value = response.data.details,
    modelPrices.value = response.data.prices
    modelAccuracy.value = response.data.modelAccuracy

    // Indicate that the model exists to show the model display
    modelExists.value = true;

    console.log('Finished loading model.')
    toast.add({ severity: 'success', summary: 'Forecast Generated', detail: 'An LSTM forecast has been generated.', life: 3000 });
    loadingModel.value = false
  }).catch((e) => {
    loadingModel.value = false
    toast.add({ severity: 'error', summary: 'Error', detail: `The forecast specified failed to generate due to the following error: ${e}.`, life: 3000 });
    console.log(`An error occurred: ${e}.`)
  })
}
</script>

<template>
  <Toast/>
  <header>
    <NavHeader />
  </header>
  <main>
      <div class="main-panel">
        <div class="stock-form">
          <StockForm @request-model="handleRequestModel" />
        </div>
        <div class="stock-graph">
          <ProgressSpinner v-if="loadingModel"/>
          <StockPriceGraph v-if="modelExists && !loadingModel" :parameters="modelParameters" :prices="modelPrices"/>
        </div>
      </div>
      <LSTMDetails v-if="modelExists && !loadingModel && modelParameters?.modelType === 'LSTM'" :details="modelDetails" :parameters="modelParameters"/>
  </main>
</template>

<style scoped>
.main-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0.5rem 0;
  flex-wrap: wrap;
}

.stock-form {
  width: 30%;
}

.stock-graph {
  width: 60%;
}
</style>