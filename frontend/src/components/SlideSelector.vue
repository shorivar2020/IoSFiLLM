<template>
  <div class="slide_container">
    <div class="slide_name">
      <span :class="{ active: selected === '1' }">Google</span>
      <span :class="{ active: selected === '2' }">DuckDuckGo</span>
      <span :class="{ active: selected === '3' }">Bing</span>
      <span :class="{ active: selected === '4' }">Brave</span>
      <span :class="{ active: selected === '5' }">Google Scholar</span>
      <span :class="{ active: selected === '6' }">Pub Med</span>
    </div>
    <input type="range" min="1" max="6" v-model="selected" class="slider" />
  </div>
</template>

<script>
export default {

  props: {
    modelValue: {
      type: String,
      required: true
    }
  },
  computed: {
    selected: {
      get() {
        return this.modelValue; // Получение значения из родителя
      },
      set(value) {
        this.$emit('update:modelValue', value); // Отправка обновления в родительский компонент
      }
    }
  }
};
</script>

<style scoped>

/* Style for the slider container */
.slide_container {
  width: 100%;
  text-align: center;
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
}

/* Style for the slider labels (search engine names) */
.slide_name {
  display: flex;
  justify-content: space-between;
  padding-top: 15px;
  width: 80%;
}

/* Style for each individual label */
.slide_name span {
  width: 16%;
  text-align: center;
}

/* Active class for the first slider */
.active {
  font-weight: bold;
}

/* Active class for the second slider */
.active2 {
  font-weight: bold;
}

/* Style for the range slider */
.slider {
  -webkit-appearance: none;
  appearance: none;
  width: 80%;
  height: 25px;
  background: #d3d3d3;
  outline: none;
  opacity: 0.7;
  transition: opacity .2s;
  border-radius: 10px;
}

/* Style for the slider hover effect */
.slider:hover {
  opacity: 1;
}

/* Style for the slider thumb */
.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16%;
  height: 25px;
  background: #000000;
  cursor: pointer;
  border-radius: 10px;
}

/* Style for the Firefox slider thumb */
.slider::-moz-range-thumb {
  width: 16%;
  height: 25px;
  background: #000000;
  cursor: pointer;
  border-radius: 10px;
}

@media only screen and (max-width: 600px) {
  .slide_name{
    font-size: 10px;
  }

  .send-button svg{
    width: 9px;
    height: 9px;
  }
  .source_container th:first-child, td:first-child {
    width: 50%;
  }

  footer{
    display: none;
  }
}
</style>
