<template>
  <div v-if="source" class="source_container">
    <table>
      <thead>
          <tr>
            <th colspan="3">
              <input type="text" class="filter" id="filterGlobal" v-model="filterGlobal" placeholder="">
            </th>
          </tr>
          <tr>
            <th>Source</th>
            <th>Year</th>
            <th>Author</th>
          </tr>
        </thead>
      <tbody>
          <tr v-for="(article, index) in filteredArticles" :key="index">
            <td>
              <details>
                <summary><a :href="article.url" target="_blank" rel="noopener noreferrer">{{ article.source }}</a></summary>
                <p>{{ article.abstract }}</p>
              </details>
            </td>
            <td>
              <p>{{ article.year }}</p>
            </td>
            <td>
              <p v-if="article.authors">Authors: {{ article.authors }}</p>
            </td>
          </tr>
        </tbody>
    </table>
  </div>
</template>

<script>
export default {
  props: ['articles', 'source'],
  data() {
    return {
      filterYear: '',    // Filter year input
      filterAuthor: '',  // New filter for author
      filterTitle: '',
      filterGlobal: "",
    }
  },
  computed: {
    filteredArticles() {
      const filter = this.filterGlobal.toLowerCase();
      return this.articles.filter(article => {
        const matchesSource = article.source.toLowerCase().includes(filter);
        const matchesYear = article.year.toString().includes(filter);
        const matchesAuthor = Array.isArray(article.authors)
          ? article.authors.join(", ").toLowerCase().includes(filter)
          : (article.authors || "").toLowerCase().includes(filter);
        const matchesAbstract = article.abstract
          ? article.abstract.toLowerCase().includes(filter)
          : false;

        return matchesSource || matchesYear || matchesAuthor || matchesAbstract;
      });
    },
  },
};
</script>

<style scoped>
.source_container th:first-child, td:first-child {
  width: 60%;
}

.source-list li {
  margin-bottom: 5px;
}

.source-list a {
  color: #000000;
  text-decoration: none;
}

.source-list a:hover {
  text-decoration: underline;
}
.source_container{
  display: flex;
  justify-content: center;
  margin-top: 15px;
  margin-bottom: 15px;
}

.source_container table{
  width: 80%;
  border: 1px solid #ddd;
  border-radius: 5px;
  //padding-top: 10px;
  //padding-bottom: 10px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  table-layout: fixed;
}

.source_container a{
  text-decoration: none;
  color: #000000;
  opacity: 0.7;
  transition: opacity .2s;
}

.source_container .filter{
  background-image: url('../../public/search_icon.png'); /* Path to the search icon */
  background-repeat: no-repeat; /* Prevents the icon from repeating */
  background-position: 10px center; /* Positions the icon inside the input field */
  background-size: 18px 18px; /* Adjusts the size of the icon */
  padding-left: 40px; /* Creates space for the icon */

  width: 90%;
  border-color: #cdc7c7;
  border-radius: 5px;
  font-size: large;
}

thead {
  position: sticky;
  top: 0;
  z-index: 1;

}

tbody{
  max-height: 400px;
  display: block;
  overflow-y: auto;
  //display: flex;
  //flex-direction: column;
}

tr:nth-child(even) {
  background-color: #cdc7c7;
}

.source_container td{
  padding: 10px;
  word-wrap: break-word;
}

tr{
  display: table;
  width: 100%;
  table-layout: fixed;
  border-bottom: 1px solid #ddd;
}

@media only screen and (max-width: 600px) {
  .send-button{
    padding: 6px 8px;
  }

  .send-button svg{
    width: 9px;
    height: 9px;
  }
  .source_container th:first-child, td:first-child {
    width: 50%;
  }
  .filter{
    width: 100%;
  }
  footer{
    display: none;
  }
}
</style>
