import axios from "axios";

const baseURL =
  process.env.REACT_APP_API_BASE_URL?.trim() || "http://localhost:8000";

const axiosClient = axios.create({
  baseURL,
});

export default axiosClient;
