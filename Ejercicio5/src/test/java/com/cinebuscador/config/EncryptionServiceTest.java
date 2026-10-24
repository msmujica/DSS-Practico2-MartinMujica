package com.cinebuscador.config;

import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;

import static org.junit.jupiter.api.Assertions.*;

class EncryptionServiceTest {

    @Test
    void debeGenerarUnHashBCrypt() throws Exception {
        String password = "ClaveSegura123";

        // Buscamos el metodo hashPassword por su nombre.
        Method hashPassword = EncryptionService.class
                .getMethod("hashPassword", String.class);

        // null indica que el metodo es estatico.
        String hash = (String) hashPassword.invoke(
                null,
                password
        );

        // El resultado debe existir, ser diferente de la password original y tener el prefijo de BCrypt.
        assertNotNull(hash);
        assertNotEquals(password, hash);
        assertTrue(hash.startsWith("$2"));
    }

    @Test
    void mismaPasswordDebeGenerarHashesDiferentes()
            throws Exception {

        String password = "ClaveSegura123";

        Method hashPassword = EncryptionService.class
                .getMethod("hashPassword", String.class);

        // Generamos dos hashes a partir de la misma password.
        String primerHash = (String) hashPassword.invoke(
                null,
                password
        );

        String segundoHash = (String) hashPassword.invoke(
                null,
                password
        );

        // BCrypt utiliza un salt aleatorio, por eso los hashes generados deben ser diferentes.
        assertNotEquals(primerHash, segundoHash);
    }

    @Test
    void debeVerificarLaPasswordCorrectamente()
            throws Exception {

        String password = "ClaveSegura123";

        // Obtenemos los metodos de generacion y verificacion.
        Method hashPassword = EncryptionService.class
                .getMethod("hashPassword", String.class);

        Method verifyPassword = EncryptionService.class
                .getMethod(
                        "verifyPassword",
                        String.class,
                        String.class
                );

        // Generamos un hash para la password correcta.
        String hash = (String) hashPassword.invoke(
                null,
                password
        );

        // La password original debe coincidir con el hash.
        boolean passwordCorrecta = (boolean) verifyPassword.invoke(
                null,
                password,
                hash
        );

        // Una password diferente no debe coincidir con el hash.
        boolean passwordIncorrecta = (boolean) verifyPassword.invoke(
                null,
                "ClaveIncorrecta",
                hash
        );

        assertTrue(passwordCorrecta);
        assertFalse(passwordIncorrecta);
    }

    @Test
    void noDebeExistirUnMetodoParaDescifrarPasswords() {
        // Un hash de password se verifica, pero no se descifra.
        // Por eso el metodo decrypt no debe estar disponible.
        assertThrows(
                NoSuchMethodException.class,
                () -> EncryptionService.class.getMethod(
                        "decrypt",
                        String.class
                )
        );
    }
}