// Delete Venue
const deleteVenue = async () => {
  const deleteButton = document.getElementById('delete-venue');

  const { id } = deleteButton.dataset;

  const result = await fetch(`/venues/${id}`, {
    method: 'DELETE'
  });

  if (result.status === 200) window.location.replace('/');
};

// Mobile hamburger menu
const openBurger = () => {
  const opener = document.querySelector('.navbar-toggle .fas');
  const navbar = document.querySelector('.navbar');

  navbar.classList.toggle('mobile');

  opener.classList.toggle('fa-bars');
  opener.classList.toggle('fa-times');
};
