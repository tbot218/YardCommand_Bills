import axiosClient from "./axiosClient";

const clientsApi = {
  getAll: () => axiosClient.get("/clients"),
  create: (data) => axiosClient.post("/clients", data),
  update: (id, data) => axiosClient.put(`/clients/${id}`, data),
  archive: (id) => axiosClient.post(`/clients/${id}/archive`),
};

export default clientsApi;
