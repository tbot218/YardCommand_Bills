import axiosClient from "./axiosClient";

const billsApi = {
  getAll: () => axiosClient.get("/bills"),
  create: (data) => axiosClient.post("/bills", data),
  update: (id, data) => axiosClient.put(`/bills/${id}`, data),
};

export default billsApi;
