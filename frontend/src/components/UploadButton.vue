
<template>
  <div class="tooltip" data-tooltip="Upload files for adding to context">
      <button class="send-button" @click="selectAndUploadFiles">
      <img
         src="../../public/upload-sign-svgrepo-com.png"
         alt="Upload_icon"
         width="18px"
         height="18px"
      ></button>
    </div>
  <input
    type="file"
    ref="fileInput"
    @change="uploadFiles"
    style="display: none;"
  />
  <div v-if="uploading">
          <div v-if="loading" class="loader"></div>
        </div>
  <div v-if="uploadError" class="popup-overlay">
      <div class="popup-content">
        <p>An error occurred during upload!</p>
        <button @click="uploadError = false">Close</button>
      </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  data() {
    return{
      fileContent: '',  // To store the file content temporarily
      fileName: 'example.txt',  // File name for the download
      selectedFiles: [],
      uploading: false,
      uploadError: false,
      uploadSuccess: false,
      files_content: [],
      files_name: [],
    }
  },
  methods: {
    selectAndUploadFiles() {
      // Programmatically trigger file input click
      this.$refs.fileInput.click();
    },
    async uploadFiles(event) {
      // Get the file from the input field
      this.selectedFiles = Array.from(event.target.files);

      if (!this.selectedFiles.length) {
        alert("Please select at least one file to upload");
        return;
      }

      const formData = new FormData();
      this.selectedFiles.forEach((file, index) => {
        formData.append(`file_${index}`, file);
      });

      this.uploading = true;
      this.uploadError = false;
      this.uploadSuccess = false;

      try {
        const response = await axios.post('http://127.0.0.1:8080/api/download', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        console.log(response.status)
        console.log(response.data)
        if (response.status === 200) {
          this.uploadSuccess = true;
          console.log('Response from server:', response.data);
          this.files_content = [...this.files_content, ...response.data.files_content];
          this.files_name = [...this.files_name, ...response.data.files_name];

          this.$emit('files-uploaded', {
          files_content: this.files_content,
          files_name: this.files_name,
        });
        }
      } catch (error) {
        this.uploadError = true;
      } finally {
        this.uploading = false;
      }
    },
  }
}
</script>

<style>
.send-button {
  background-color: #000000;
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  margin-left: 10px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
    opacity: 0.7;
  transition: opacity .2s;
  height: 100%;
}

.send-button:hover {
  opacity: 1;
}

.send-button svg {
  width: 18px;
  height: 18px;
}


.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-content {
  background: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.popup-content button{
  background-color: #000000;
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  margin-left: 10px;
  cursor: pointer;
  font-size: 16px;
  opacity: 0.7;
  transition: opacity .2s;
}

.popup-content button:hover {
  opacity: 1;
}


.tooltip {
  position: relative;
  display: inline-block;
}

.tooltip::after {
  content: attr(data-tooltip);
  visibility: hidden;
  opacity: 0;
  background-color: #333;
  color: #fff;
  text-align: center;
  padding: 5px;
  border-radius: 5px;
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1;
  transition: opacity 0.3s;
  font-size: 12px;
  white-space: nowrap;
}

.tooltip:hover::after {
  visibility: visible;
  opacity: 1;
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

  footer{
    display: none;
  }
}
</style>