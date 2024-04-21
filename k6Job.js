import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
    vus: 1, // This will be dynamically adjusted by the Node.js script
    duration: '60s', // Consider making this shorter if you want quicker feedback per stage
    noVUConnectionReuse: false,
};

const urls = [
    'http://localhost:8080/tools.descartes.teastore.webui/category?category=2&page=1',
    'http://localhost:8080/tools.descartes.teastore.webui/category?category=3&page=1',
    'http://localhost:8080/tools.descartes.teastore.webui/category?category=4&page=1',
    'http://localhost:8080/tools.descartes.teastore.webui/product?id=207',
    'http://localhost:8080/tools.descartes.teastore.webui/category?category=6&page=1'
];

export default function () {
    const url = urls[Math.floor(Math.random() * urls.length)];

    http.get(url);
    sleep(1);
}