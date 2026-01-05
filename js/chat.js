document.addEventListener('DOMContentLoaded', function() {
    const startChatButton = document.querySelector('.start-chat-btn'); // Assurez-vous que votre bouton a cette classe

    if (startChatButton) {
        startChatButton.addEventListener('click', function(e) {
            e.preventDefault();
            openChatWindow();
        });
    }

    function openChatWindow() {
        // Logique pour ouvrir le chat
        console.log("Le chat démarre...");
        
        // Exemple : Ouvrir une fenêtre modale ou un widget tiers
        // Si vous utilisez un service tiers (ex: Tawk.to, Intercom), appelez leur API ici.
        // window.Tawk_API.toggle(); 
        
        alert("La fenêtre de chat s'ouvre ! (Fonctionnalité à connecter à votre service de chat)");
    }
});
