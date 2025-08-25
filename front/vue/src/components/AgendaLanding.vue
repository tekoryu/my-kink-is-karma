<template>
  <v-app>
    <v-main>
      <v-container fluid class="pa-0">


        <!-- Main Content -->
        <v-container class="py-8">
          <!-- Refresh Button -->
          <v-row justify="end" class="mb-4">
            <v-btn
              color="primary"
              variant="outlined"
              prepend-icon="mdi-refresh"
              @click="refreshData"
            >
              Atualizar Dados
            </v-btn>
          </v-row>
          <!-- Loading State -->
          <v-row v-if="loading" justify="center">
            <v-col cols="12" class="text-center">
              <v-progress-circular
                indeterminate
                color="primary"
                size="64"
              ></v-progress-circular>
              <div class="text-h6 mt-4">Carregando dados da agenda...</div>
            </v-col>
          </v-row>

          <!-- Error State -->
          <v-row v-else-if="error" justify="center">
            <v-col cols="12" md="8" class="text-center">
              <v-alert
                type="error"
                variant="tonal"
                class="mb-4"
              >
                {{ error }}
              </v-alert>
              <v-btn color="primary" @click="loadData">
                Tentar Novamente
              </v-btn>
            </v-col>
          </v-row>

          <!-- Summary Content -->
          <div v-else>
            <!-- Summary Cards -->
            <v-row class="mb-8">
              <v-col cols="12" md="4">
                <v-card class="text-center" color="primary" dark>
                  <v-card-text>
                    <div class="text-h2 font-weight-bold">{{ summaryData.eixos?.length || 0 }}</div>
                    <div class="text-h6">Eixos Estratégicos</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="4">
                <v-card class="text-center" color="secondary" dark>
                  <v-card-text>
                    <div class="text-h2 font-weight-bold">{{ summaryData.temas?.length || 0 }}</div>
                    <div class="text-h6">Temas</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="4">
                <v-card class="text-center" color="accent" dark>
                  <v-card-text>
                    <div class="text-h2 font-weight-bold">{{ summaryData.proposicoes?.length || 0 }}</div>
                    <div class="text-h6">Proposições</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <!-- Summary List -->
            <v-card>
              <v-card-title class="text-h5 font-weight-bold">
                Resumo da Agenda Legislativa
              </v-card-title>
              <v-card-text>
                                 <v-expansion-panels variant="accordion">
                   <!-- Eixos Section -->
                   <v-expansion-panel>
                     <v-expansion-panel-title>
                       <v-icon start>mdi-axis-arrow</v-icon>
                       Eixos Estratégicos ({{ summaryData.eixos?.length || 0 }})
                     </v-expansion-panel-title>
                     <v-expansion-panel-text>
                       <div class="list-container">
                         <v-list>
                           <v-list-item
                             v-for="eixo in summaryData.eixos"
                             :key="eixo.id"
                             :title="eixo.nome"
                             :subtitle="`${eixo.temas_count || 0} temas`"
                           >
                             <template v-slot:prepend>
                               <v-icon color="primary">mdi-circle</v-icon>
                             </template>
                           </v-list-item>
                         </v-list>
                       </div>
                     </v-expansion-panel-text>
                   </v-expansion-panel>

                   <!-- Temas Section -->
                   <v-expansion-panel>
                     <v-expansion-panel-title>
                       <v-icon start>mdi-tag</v-icon>
                       Temas ({{ summaryData.temas?.length || 0 }})
                     </v-expansion-panel-title>
                     <v-expansion-panel-text>
                       <div class="list-container">
                         <v-list>
                           <v-list-item
                             v-for="tema in summaryData.temas"
                             :key="tema.id"
                             :title="tema.nome"
                             :subtitle="`Eixo: ${tema.eixo_nome} | ${tema.proposicoes_count || 0} proposições`"
                           >
                             <template v-slot:prepend>
                               <v-icon color="secondary">mdi-tag</v-icon>
                             </template>
                           </v-list-item>
                         </v-list>
                       </div>
                     </v-expansion-panel-text>
                   </v-expansion-panel>

                   <!-- Proposições Section -->
                   <v-expansion-panel>
                     <v-expansion-panel-title>
                       <v-icon start>mdi-file-document</v-icon>
                       Proposições ({{ summaryData.proposicoes?.length || 0 }})
                     </v-expansion-panel-title>
                     <v-expansion-panel-text>
                       <div class="list-container">
                         <v-list>
                           <v-list-item
                             v-for="proposicao in summaryData.proposicoes"
                             :key="proposicao.id"
                             :title="`${proposicao.tipo} ${proposicao.numero}/${proposicao.ano}`"
                             :subtitle="`${proposicao.tema_nome} | ${proposicao.tema_eixo_nome}`"
                           >
                             <template v-slot:prepend>
                               <v-icon color="accent">mdi-file-document</v-icon>
                             </template>
                             <template v-slot:append>
                               <v-chip
                                 v-if="proposicao.autor"
                                 size="small"
                                 color="info"
                                 variant="outlined"
                               >
                                 {{ proposicao.autor }}
                               </v-chip>
                             </template>
                           </v-list-item>
                         </v-list>
                       </div>
                     </v-expansion-panel-text>
                   </v-expansion-panel>
                 </v-expansion-panels>
              </v-card-text>
            </v-card>
          </div>
        </v-container>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { agendaApi } from '../services/api'

const loading = ref(true)
const error = ref(null)
const summaryData = ref({
  eixos: [],
  temas: [],
  proposicoes: []
})

const loadData = async () => {
  try {
    loading.value = true
    error.value = null
    const data = await agendaApi.getSummary()
    summaryData.value = data
  } catch (err) {
    console.error('Error loading data:', err)
    error.value = 'Erro ao carregar dados da agenda. Verifique a conexão com o servidor.'
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.v-expansion-panels {
  max-width: 100%;
}

.list-container {
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
}

.list-container::-webkit-scrollbar {
  width: 8px;
}

.list-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.list-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.list-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Ensure the expansion panel content doesn't overflow */
.v-expansion-panel-text {
  max-height: none !important;
}

/* Make sure the main container allows scrolling */
.v-main {
  overflow-y: auto;
}
</style>
