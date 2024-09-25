//src/services/AxiosInstance.jsx
import axios from "axios";

const axiosInstance = axios.create({
  baseURL: "http://127.0.0.1:8000/api/", 
  headers: {
    'Authorization':'Bearer ' + localStorage.getItem('token')?.access,
    "Content-Type": "application/json",
  },
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token && !config.url.includes("/login/")) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log("Token added to request headers:", config.headers.Authorization);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default axiosInstance;
