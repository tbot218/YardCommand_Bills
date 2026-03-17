import axiosClient from "./axiosClient";

const billsApi = {
  getAll: () => axiosClient.get("/bills"),
  create: (data) => axiosClient.post("/bills", data),
};

export default billsApi;
