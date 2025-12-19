<script setup>
import {Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend} from 'chart.js'
import { Line } from 'vue-chartjs'
import { ref } from 'vue';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip,Legend)

const props = defineProps(['parameters', 'prices']);
const graphChoice = ref('All Prices')
const graphOptions = ref(['All Prices', 'Historical', 'Forecasted'])
const realizedColour = '#23cbed'
const forecastedColour = '#eda323'

const getRealizedData = () => {
  return {
  labels: props.prices.realized.date,
  datasets: [
    {
      label: "Close Prices (Historical)",
      backgroundColor: realizedColour,
      data: props.prices.realized.prices,
    },
  ]
  }
}

const getForecastedData = () => {
  return {
  labels: props.prices.forecasted.date,
  datasets: [
    {
      label: "Close Prices (Forecasted)",
      backgroundColor: forecastedColour,
      data: props.prices.forecasted.prices,
    },
  ]
  }
}

const getCombinedData = () => {
  return {
  labels: getCombinedDates(),
  datasets: [
    {
      label: "Close Prices (Historical & Forecasted)",
      backgroundColor: getPointColours(),
      data: getCombinedPrices(),
    },
  ]
  }
}

// Chooses different colours for realized vs forecasted points
const getPointColours = (pointInfo) => {
  const pointColours = []

  for (let i = 0; i < props.prices.realized.prices.length; ++i) {
    pointColours.push(realizedColour)
  }

  for (let i = 0; i < props.prices.forecasted.prices.length; ++i) {
    pointColours.push(forecastedColour)
  }

  return pointColours
}



const getCombinedDates = () => {
  return [...props.prices.realized.date, ...props.prices.forecasted.date]
}

const getCombinedPrices = () => {
  return [...props.prices.realized.prices, ...props.prices.forecasted.prices]
}

const getOptions = () => {
  return {
  }
}

</script>

<template>
    <h2>Stock Prices</h2>
    <Line v-if="graphChoice === 'All Prices'" :data="getCombinedData()" :options="getOptions()"/>
    <Line v-else-if="graphChoice === 'Historical'" :data="getRealizedData()" :options="getOptions()"/>
    <Line v-else :data="getForecastedData()" :options="getOptions()"/>
    <SelectButton id="graphInput" v-model="graphChoice" :options="graphOptions"/>
</template>