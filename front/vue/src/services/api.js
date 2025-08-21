import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export const agendaApi = {
  // Fetch all eixos with their temas count
  getEixos: async () => {
    const response = await api.get('/bi/eixos/')
    return response.data
  },

  // Fetch all temas with their proposicoes count
  getTemas: async () => {
    const response = await api.get('/bi/temas/')
    return response.data
  },

  // Fetch all proposicoes with full details
  getProposicoes: async () => {
    const response = await api.get('/bi/proposicoes/')
    return response.data
  },

  // Fetch summary data (eixos, temas, proposicoes)
  getSummary: async () => {
    const [eixos, temas, proposicoes] = await Promise.all([
      agendaApi.getEixos(),
      agendaApi.getTemas(),
      agendaApi.getProposicoes()
    ])
    
    return {
      eixos,
      temas,
      proposicoes
    }
  }
}

export default api
