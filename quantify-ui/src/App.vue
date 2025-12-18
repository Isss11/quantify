<script setup>
import axios from 'axios';
import { ref } from 'vue';
import LSTMDetails from './components/LSTMDetails.vue';

const modelParameters = ref('')
const modelDetails = ref('')
const modelPrices = ref('');
const modelAccuracy = ref('')
const modelExists = ref(false);
const loadingModel = ref(false)

// Requests to forecast financial data
const handleRequestModel = (e, inputTicker, inputForecastPeriod, chosenModel, startDate, lookBack, epochs, batchSize) => {
  loadingModel.value = true

  axios.post("http://127.0.0.1:8000/lstmForecast/", {
    ticker: inputTicker,
    forecastLength: inputForecastPeriod,
    sampleStartDate: startDate,
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

    console.log('Finished loading model')
    loadingModel.value = false
  })
}
</script>

<template>
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