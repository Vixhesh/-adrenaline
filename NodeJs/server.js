const express = require("express");
const jwt = require("jsonwebtoken");

const app = express();
const secret = process.env.SECRET_KEY; 

app.use(express.static("public"));

app.get("/", (req, res) => {
    const token = req.query.token;

    try {
        jwt.verify(token, secret);
        res.sendFile(__dirname + "/public/index.html");
    } catch {
        res.status(401).send("Unauthorized");
    }
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => console.log(`Game server running on ${PORT}`));