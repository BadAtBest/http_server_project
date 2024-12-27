function navigateToProject() {
    const project = document.getElementById("project-select").value;
    if (project) {
        // Navigate to the selected project's page (e.g., /project1)
        window.location.href = `/${project}`;
    }
}
