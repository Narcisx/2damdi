/**
 * DATA DE LA HISTORIA
 * Estructura de nodos para la narrativa interactiva.
 */
const storyData = {
    // --- ENTRADA (Punto de inicio) ---
    inicio: {
        text: "Año 2084. La lluvia ácida golpea tu casco. Estás frente a la Megatorre 'Aethelgard'. Tu contacto dice que el chip está en el piso 99.",
        color: "#1a1a2e",
        image: "inicio.png",
        choices: [
            { text: "Entrar por el vestíbulo (Riesgo alto)", next: "lobby" },
            { text: "Trepar por los conductos (Sigilo)", next: "ventilacion" },
            { text: "Hackear un dron de carga (Ingeniería)", next: "azotea" }
        ]
    },

    // --- RAMA DEL VESTÍBULO ---
    lobby: {
        text: "El vestíbulo brilla con mármol sintético. Una recepcionista androide te mira. '¿Tiene una cita, ciudadano?'",
        color: "#16213e",
        image: "lobby.png",
        choices: [
            { text: "Mostrar credenciales falsas", next: "chequeo_datos" },
            { text: "Provocar una distracción", next: "distraccion" }
        ]
    },
    distraccion: {
        text: "Lanzas un señuelo sónico al otro lado de la sala. Los guardias corren hacia allí. El camino a los ascensores está libre.",
        color: "#1b1b2f",
        image: "distraccion.png",
        choices: [
            { text: "Correr al ascensor", next: "persecucion" }
        ]
    },
    chequeo_datos: {
        text: "La androide procesa los datos. Sus ojos parpadean en rojo. 'Estas credenciales pertenecen a un empleado fallecido'.",
        color: "#c0392b",
        image: "chequeo.png",
        choices: [
            { text: "Correr hacia los ascensores", next: "persecucion" },
            { text: "Desactivar a la androide", next: "combate_cercano" }
        ]
    },
    combate_cercano: {
        text: "Con un movimiento rápido, cortocircuitas el cuello de la androide. Cae al suelo antes de activar la alarma. Te deslizas hacia las sombras.",
        color: "#2c3e50",
        image: "combatecercano.png",
        choices: [
            { text: "Ir a la sala de servidores", next: "sigilo" }
        ]
    },

    // --- RAMA DE VENTILACIÓN ---
    ventilacion: {
        text: "El aire aquí es espeso. Llegas a una bifurcación: un camino lleva a los servidores, el otro parece un laboratorio oculto.",
        color: "#0f3460",
         image: "ventilacion.png",
        choices: [
            { text: "Ir a la Sala de Servidores", next: "sigilo" },
            { text: "Investigar el Laboratorio", next: "laboratorio_secreto" }
        ]
    },
    laboratorio_secreto: {
        text: "Encuentras un prototipo de camuflaje óptico. Podría hacerte invisible, pero activará una alarma silenciosa.",
        color: "#533483",
        image: "laboratorio.png",
        choices: [
            { text: "Robar el prototipo", next: "invisibilidad" },
            { text: "Ignorarlo y seguir al núcleo", next: "sigilo" }
        ]
    },

    // --- RAMA DE LA AZOTEA ---
    azotea: {
        text: "El viento sopla fuerte. Estás en la cima. Una puerta de alta seguridad te separa del núcleo de datos.",
        color: "#1b1b2f",
        image: "azotea.png",
        choices: [
            { text: "Cortar la energía del piso", next: "apagon" },
            { text: "Usar un exploit en el panel", next: "hackeo_azotea" }
        ]
    },
    hackeo_azotea: {
        text: "Tus dedos vuelan sobre la consola. El firewall de la torre cae y la puerta se desliza suavemente. Estás dentro.",
        color: "#16213e",
        image: "hackeoazotea.png",
        choices: [
            { text: "Bajar al núcleo de datos", next: "sigilo" }
        ]
    },

    // --- NUDO INTERMEDIO (Escenas de transición) ---
    persecucion: {
        text: "¡Los drones de seguridad te pisan los talones! El ascensor está cerrándose justo frente a ti.",
        color: "#e94560",
        image: "persecucion.png",
        choices: [
            { text: "Saltar dentro del ascensor", next: "combate_ascensor" },
            { text: "Usar granada de pulso", next: "escape_exitoso" }
        ]
    },
    combate_ascensor: {
        text: "Logras entrar, pero un dron se cuela contigo. Es una lucha frenética en un espacio cerrado mientras el ascensor sube.",
        color: "#533483",
         image: "combateascensor2.png",
        choices: [
            { text: "Destruir al dron", next: "sigilo" },
            { text: "Ser superado por el dron", next: "soborno_fallido" }
        ]
    },
    sigilo: {
        text: "Avanzas por las sombras del núcleo. Ves al CEO hablando con un holograma sobre el 'Protocolo de Purga'. Es ahora o nunca.",
        color: "#16213e",
        image: "sigilo.png",
        choices: [
            { text: "Descargar los datos en silencio", next: "final_bueno" },
            { text: "Enfrentar al CEO cara a cara", next: "confrontacion" }
        ]
    },

    // --- FINALES ---
    final_bueno: {
        text: "FINAL: Misión cumplida. Tienes las pruebas de los crímenes corporativos. Mañana, el mundo despertará.",
        color: "#27ae60",
        image: "finalbueno.png",
        choices: [{ text: "Volver a jugar", next: "inicio" }]
    },
    invisibilidad: {
        text: "FINAL: El prototipo te hace indetectable. Escapas con el chip y la tecnología. Eres la nueva leyenda del ciberespacio.",
        color: "#f1c40f",
        image: "invisibilidad.png",

        choices: [{ text: "Volver a jugar", next: "inicio" }]
    },
    confrontacion: {
        text: "FINAL: El CEO te ofrece unirte a ellos a cambio de una fortuna. Aceptas. Te has convertido en lo que juraste destruir.",
        color: "#8e44ad",
        image: "confrontacion.png",

        choices: [{ text: "Volver a jugar", next: "inicio" }]
    },
    soborno_fallido: {
        text: "FINAL: Te han capturado. Te espera una vida de trabajos forzados en las colonias mineras de Marte.",
        color: "#000",
        image: "sobornofallido.png",

        choices: [{ text: "Reintentar misión", next: "inicio" }]
    },
    escape_exitoso: {
        text: "FINAL: La granada EMP fríe los drones. Escapas por el tejado mientras el edificio se sume en el caos.",
        color: "#2980b9",
          image: "escapeexitoso.png",
        choices: [{ text: "Volver a jugar", next: "inicio" }]
    },
    apagon: {
        text: "FINAL: El apagón alerta a todo el edificio. La seguridad te rodea en la oscuridad. No hay salida para ti.",
        color: "#2c3e50",
          image: "apagon.png",
        choices: [{ text: "Fin del juego - Reintentar", next: "inicio" }]
    }
};

const comicEngine = {
    textElement: document.getElementById('scene-text'),
    imageElement: document.getElementById('scene-image'),
    choicesContainer: document.getElementById('choices'),
    
    // VARIABLES DE CONTROL
    currentSceneId: null,
    typeInterval: null,
    isTyping: false,

    renderScene(sceneId) {
        const scene = storyData[sceneId];
        if (!scene) return;

        // Guardamos el ID actual para poder "saltar" luego
        this.currentSceneId = sceneId;

        // 1. Imagen
       if (scene.image) {
    this.imageElement.style.backgroundImage = `url('${scene.image}')`;
    this.imageElement.style.backgroundSize = "contain"; // Imagen completa
    this.imageElement.style.backgroundPosition = "center";
    this.imageElement.style.backgroundRepeat = "no-repeat";
    this.imageElement.innerHTML = '';
} else {
            this.imageElement.style.backgroundColor = scene.color || "#333";
            this.imageElement.innerHTML = `<div class="placeholder-img">ESCENA: ${sceneId.toUpperCase()}</div>`;
        }

        // 2. Preparar texto
        this.choicesContainer.innerHTML = '';
        this.textElement.textContent = ""; 
        this.isTyping = true; // Marcamos que está escribiendo
        
        let i = 0;
        const fullText = scene.text;

        if (this.typeInterval) clearInterval(this.typeInterval);

        this.typeInterval = setInterval(() => {
            this.textElement.textContent += fullText[i];
            i++;

            if (i >= fullText.length) {
                this.finishTyping(scene);
            }
        }, 20);
    },

    // Función para finalizar el proceso de escritura
    finishTyping(scene) {
        clearInterval(this.typeInterval);
        this.textElement.textContent = scene.text; // Asegura texto completo
        this.isTyping = false;
        this.createButtons(scene.choices);
    },

    createButtons(choices) {
        this.choicesContainer.innerHTML = '';
        choices.forEach((choice, index) => {
            const button = document.createElement('button');
            button.innerText = choice.text;
            button.classList.add('btn-appear');
            button.style.animationDelay = `${index * 0.15}s`;
            button.onclick = () => this.renderScene(choice.next);
            this.choicesContainer.appendChild(button);
        });
    },

    init() {
        if (!this.textElement || !this.choicesContainer) return;

        // EVENTO PARA SALTAR TEXTO:
        // Al hacer clic en el panel del cómic, si está escribiendo, termina de golpe.
        document.getElementById('comic-panel').addEventListener('click', () => {
            if (this.isTyping) {
                const scene = storyData[this.currentSceneId];
                this.finishTyping(scene);
            }
        });

        this.renderScene('inicio');
    }
};

document.addEventListener('DOMContentLoaded', () => comicEngine.init());